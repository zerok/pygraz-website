from flask import g, render_template
import time
import datetime
import pytz

from . import exceptions


class DocumentLock(object):
    """
    This is a simple context manager that requires that the user has a lock
    on the document to be edited. The document is represented by the id
    or root_id passed as string.

    If no such lock exists, the manager creates that lock.
    """
    def __init__(self, key, timeout=None):
        if isinstance(key, basestring):
            self.key = key
        elif hasattr(key, 'id'):
            self.key = '%s:id=%s' % (str(key.__class__), str(key.id))
        else:
            self.key = str(key)
        self.success = False
        self.lock_key = 'locks:' + self.key
        self.timeout = 300
        if timeout is not None:
            self.timeout = timeout
        self.attempt = 0

    def __enter__(self):
        lockinfo = dict([
                (self.lock_key + ':holder', g.user.id),
                (self.lock_key + ':expires', time.time() + self.timeout)])
        if g.redis.msetnx(lockinfo):
            self.success = True
            return self

        lock_user, lock_timeout = g.redis.mget([self.lock_key + ':holder',
            self.lock_key + ':expires'])

        if float(lock_timeout) < time.time():
            # Found expired keys. Delete them and retry
            g.redis.delete(*lockinfo.keys())
            if self.attempt > 5:
                raise exceptions.Conflict()
            self.attempt += 1
            return self.__enter__()  # Retry

        if lock_user != str(g.user.id):
            raise exceptions.Conflict()

        g.redis.set(self.lock_key + ':expires',
                time.time() + self.timeout)
        self.success = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self.success:
            self.unlock()

    def unlock(self):
        g.redis.delete(self.lock_key + ":holder")
        g.redis.delete(self.lock_key + ":expires")


def to_doc_value(field):
    import flatland
    if isinstance(field, flatland.DateTime):
        return field.value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return field.value


def handle_conflict(*args, **kwargs):
    return render_template('errors/conflict.html')


def is_editor_for(doc, user=None):
    """
    Checks if the given user has editor status for the given document
    (determined by the user's editor_of property and the doc's root_id)
    """
    if user is None:
        user = g.user
    if user is None:
        return False
    if user.is_admin:
        return True
    return hasattr(doc, "author") and doc.author == user


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

import pygraz_website as site
from flask import g, abort, render_template
import time, datetime

from . import exceptions, filters


class DocumentLock(object):
    """
    This is a simple context manager that requires that the user has a lock
    on the document to be edited. The document is represented by the id
    or root_id passed as string.

    If no such lock exists, the manager creates that lock.
    """
    def __init__(self, key, timeout=None):
        self.key = key
        self.success = False
        self.lock_key = 'locks.' + key
        self.timeout = 300
        if timeout is not None:
            self.timeout = timeout
        self.attempt = 0

    def __enter__(self):
        lockinfo = dict([
                (self.lock_key + '.holder', g.user['_id']),
                (self.lock_key + '.expires', time.time() + self.timeout)
                ])
        if site.redis.msetnx(lockinfo):
            self.success = True
            return self

        lock_user, lock_timeout = site.redis.mget([self.lock_key + '.holder',
            self.lock_key + '.expires'])

        if float(lock_timeout) < time.time():
            # Found expired keys. Delete them and retry
            site.redis.delete(*lockinfo.keys())
            if self.attempt > 5:
                raise exceptions.Conflict()
            self.attempt += 1
            return self.__enter__() # Retry

        if lock_user != g.user['_id']:
            raise exceptions.Conflict()

        site.redis.set(self.lock_key + '.expires',
                time.time() + self.timeout)
        self.success = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self.success:
            self.unlock()

    def unlock(self):
        site.redis.delete(self.lock_key + ".holder")
        site.redis.delete(self.lock_key + ".expires")

def save_edit(doc, form):
    """
    This creates a new document based on the existing one and updates
    all the fields from the new form.
    """
    new_doc = {}
    for prop, _ in doc.all_properties().iteritems():
        new_doc[prop] = getattr(doc, prop)
    for field in form.all_children:
        new_doc[field.name] = to_doc_value(field)
    new_doc['previous_version'] = doc._id
    if 'root_id' not in doc:
        doc['root_id'] = doc['_id']
    new_doc['root_id'] = doc['root_id']
    new_doc['updated_at'] = filters.datetimecode(datetime.datetime.utcnow())
    new_doc['updated_by'] = {'id': g.user['_id'], 'username': g.user['username']}
    new_doc['doc_type'] = doc['doc_type']
    site.couchdb.save_doc(new_doc)
    doc['next_version'] = new_doc['_id']
    doc.save()
    return doc.__class__.get(new_doc['_id'])

def save_new(form, type_):
    new_doc = {}
    for field in form.all_children:
        new_doc[field.name] = to_doc_value(field)
    new_doc['doc_type'] = type_
    new_doc['updated_at'] = filters.datetimecode(datetime.datetime.utcnow())
    new_doc['updated_by'] = {'id': g.user['_id'], 'username': g.user['username']}
    site.couchdb.save_doc(new_doc)
    new_doc['root_id'] = new_doc['_id']
    site.couchdb.save_doc(new_doc)
    return new_doc


def to_doc_value(field):
    import flatland
    if isinstance(field, flatland.DateTime):
        return field.value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return field.value

def handle_conflict(*args, **kwargs):
    return render_template('errors/conflict.html')

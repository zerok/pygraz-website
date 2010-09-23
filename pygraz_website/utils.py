import pygraz_website as site
from flask import g, abort
import time

from . import exceptions


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


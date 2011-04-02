from collections import defaultdict
from flask import Module, render_template, g

import pygraz_website as site
from pygraz_website import models


module = Module(__name__, url_prefix='/admin')

@module.route('/')
def index():
    return render_template('admin/index.html')

@module.route('/locks')
def locks():
    locks = defaultdict(dict)
    keys = g.redis.keys("locks:*")
    holders = {}
    if not keys:
        values = []
    else:
        values = g.redis.mget(keys)
    for l,v in zip(keys, values):
        _, type_, docid, field = l.split(":")
        locks[type_ + docid][field]=v
        if field == 'holder':
            holders[int(v)] = {}
    if holders:
        for user in models.User.query.filter(models.User.id.in_(map(int, holders.keys()))):
            holders[user.id] = user
    for k, v in locks.iteritems():
        v['holder'] = holders[int(v['holder'])]
    return render_template('admin/locks.html', locks=locks)

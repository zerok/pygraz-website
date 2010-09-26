from collections import defaultdict
from flask import Module, render_template

import pygraz_website as site
from pygraz_website import documents


module = Module(__name__, url_prefix='/admin')

@module.route('/')
def index():
    return render_template('admin/index.html')

@module.route('/locks')
def locks():
    locks = defaultdict(dict)
    keys = site.redis.keys("locks.*")
    holders = {}
    if not keys:
        values = []
    else:
        values = site.redis.mget(keys)
    for l,v in zip(keys, values):
        _, docid, field = l.split(".")
        locks[docid][field]=v
        if field == 'holder':
            holders[v] = {}
    if holders:
        for e in documents.User.view('_all_docs', include_docs=True, keys=holders.keys()):
            holders[e['_id']] = e
    for k, v in locks.iteritems():
        v['holder'] = holders[v['holder']]
    return render_template('admin/locks.html', locks=locks)

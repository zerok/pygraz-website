from flask import Module, request, redirect, abort, render_template
import datetime

import pygraz_website as site
from pygraz_website import documents, decorators


module = Module(__name__, url_prefix='/')

@module.route('/')
def index():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    next_meetup = documents.Meetup.view('frontend/meetups_by_date',
            descending=False, startkey=now_key, limit=1).first()
    return render_template('index.html', next_meetup=next_meetup)

@module.route('/doc/<docid>')
def view_doc(docid):
    doc = site.couchdb.get(docid)
    return globals()[doc['doc_type']](None, docid=docid)


@module.route('/purge-version/<docid>', methods=['POST', 'GET'])
@decorators.admin_required
def purge_version(docid):
    """
    Removes a version from the database. This is irreversible!
    """
    doc = documents.Version.get(docid)
    if doc is None:
        return abort(404)
    if request.method == 'POST':
        next_version = None
        prev_version = None
        if doc.next_version is not None:
            next_version = site.couchdb.get(doc.next_version)
        if doc.previous_version is not None:
            prev_version = site.couchdb.get(doc.previous_version)
        if next_version is not None and prev_version is not None:
            next_version['previous_version'] = prev_version['_id']
            prev_version['next_version'] = next_version['_id']
            next_doc = next_version['_id']
        elif next_version is not None:
            next_version['previous_version'] = None
            next_doc = next_version['_id']
        elif prev_version is not None:
            prev_version['next_version'] = None
            next_doc = prev_version['_id']
        else:
            # This is the last version of this document
            next_doc = None
        doc.delete()
        if next_version is not None:
            site.couchdb.save_doc(next_version)
        if prev_version is not None:
            site.couchdb.save_doc(prev_version)
        if next_doc is not None:
            return redirect(url_for('view_doc', docid=next_doc))
        return redirect('/')
    return render_template('confirm_purge.html')

from flask import render_template, Module, request, redirect, url_for, session
from flask import g, abort
import datetime
import couchdbkit
import copy
import functools
from flatland.out.markup import Generator

import pygraz_website as site
from . import documents, forms, filters, utils, exceptions


root = Module(__name__, url_prefix='')

def login_required(func):
    @functools.wraps(func)
    def _func(*args, **kwargs):
        if not hasattr(g, 'user'):
            return redirect(url_for('login', next=request.path))
        return func(*args, **kwargs)
    return _func

def admin_required(func):
    @functools.wraps(func)
    def _func(*args, **kwargs):
        if not hasattr(g, 'user'):
            return redirect(url_for('login', next=request.path))
        if g.user.roles is None or not 'admin' in g.user.roles:
            return abort(403)
        return func(*args, **kwargs)
    return _func

@root.context_processor
def add_form_generator():
    return {'formgen': Generator(auto_for=True)}

@root.context_processor
def auth_processor():
    result = {
            'is_logged_in': False,
            'is_admin': False
            }
    if hasattr(g, 'user') and g.user is not None:
        result['is_logged_in'] = True
        if 'admin' in g.user.roles:
            result['is_admin'] = True
    return result

@root.before_request
def check_user():
    if 'openid' in session:
        g.user = documents.User.view('frontend/users_by_openid',
                key=session['openid']).first()


@root.route('/doc/<docid>')
def view_doc(docid):
    doc = site.couchdb.get(docid)
    return globals()[doc['type']](None, docid=docid)


@root.route('/')
def index():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    next_meetup = documents.Meetup.view('frontend/meetups_by_date',
            descending=False, startkey=now_key, limit=1).first()
    return render_template('index.html', next_meetup=next_meetup)

@root.route('/meetups/')
def meetups():
    """List all meetups in chronological order"""
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=False, startkey=now_key))
            )

@root.route('/meetups/<date>')
def meetup(date, docid=None):
    if docid is None:
        doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
                include_docs=True).first()
    else:
        doc = documents.Meetup.get(docid)
        if not doc.next_version:
            return redirect(url_for('meetup', date=filters.datecode(doc.start)))
    if 'root_id' in doc:
        versions = documents.Version.view('frontend/all_versions',
                endkey=[doc['root_id']], startkey=[doc['root_id'], 'Z'],
                descending=True)
    else:
        versions = []
    return render_template('meetup.html',
            meetup = doc,
            versions=versions)

@root.route('/meetups/<date>/edit', methods=['GET', 'POST'])
@login_required
def edit_meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
            include_docs=True).first()
    with utils.DocumentLock(doc.root_id) as lock:
        if doc.next_version:
            return abort(403)
        if request.method == 'POST':
            form = forms.MeetupForm.from_flat(request.form)
            if form.validate({'doc': doc}):
                new_doc = save_edit(doc, form)
                lock.unlock()
                return redirect(url_for('meetup',
                    date=filters.datecode(new_doc.start)))
        else:
            form = forms.MeetupForm.from_object(doc)
        return render_template('meetups/edit.html',
                meetup=meetup,
                form=form)

@root.route('/create-meetup', methods=['GET','POST'])
@admin_required
def create_meetup():
    if request.method == 'POST':
        form = forms.MeetupForm.from_flat(request.form)
        if form.validate():
            save_new(form, 'meetup')
            return redirect(url_for('meetup',
                date=filters.datecode(form['start'].value)))
    else:
        form = forms.MeetupForm()
    return render_template('meetups/create.html', form=form)



@root.route('/meetups-archive/')
def meetup_archive():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups/archive.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=True, startkey=now_key, include_docs=True))
            )

@root.route('/purge-version/<docid>', methods=['POST', 'GET'])
@admin_required
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

@root.route('/account/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        form = forms.RegisterForm.from_flat(request.form)
        if form.validate():
            doc = dict(form.flatten())
            doc['openids'] = [session['openid']]
            doc['type'] = 'user'
            doc['username'] = doc['username'].lstrip().rstrip()
            site.couchdb.save_doc(doc)
            return redirect(site.oid.get_next_url())
    else:
        default = {}
        for k, v in request.args.items():
            if k == 'name':
                default['username'] = v
            else:
                default[k] = v
        form = forms.RegisterForm.from_flat(default)
    return render_template('account/register.html',
            form=form, next=site.oid.get_next_url())

@root.route('/account/login', methods=['GET','POST'])
@site.oid.loginhandler
def login():
    if request.method == 'POST':
        form = forms.LoginForm.from_flat(request.form)
        if form.validate():
            return site.oid.try_login(form['openid'].u,
                    ask_for=['fullname', 'email'])
    else:
        form = forms.LoginForm()
    return render_template('account/login.html',
            form=form, next=request.args.get('next', '/'))

@site.oid.after_login
def login_or_register(response):
    session['openid'] = response.identity_url
    user = documents.User.view('frontend/users_by_openid',
            key=session['openid']).first()
    if user is None:
        return redirect(url_for('register',
                name=response.fullname,
                email=response.email, next=site.oid.get_next_url()))
    else:
        return redirect(site.oid.get_next_url())

@root.route('/account/logout')
def logout():
    del session['openid']
    return redirect(request.args.get('next', '/'))

def handle_conflict(*args, **kwargs):
    return render_template('errors/conflict.html')

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
    site.couchdb.save_doc(new_doc)
    doc['next_version'] = new_doc['_id']
    doc.save()
    return doc.__class__.get(new_doc['_id'])

def save_new(form, type_):
    new_doc = {}
    for field in form.all_children:
        new_doc[field.name] = to_doc_value(field)
    new_doc['type'] = type_
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


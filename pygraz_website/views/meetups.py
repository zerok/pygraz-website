from flask import Module, render_template, request, redirect, url_for, current_app
import datetime

import pygraz_website as site
from pygraz_website import documents, forms, decorators, utils, filters


module = Module(__name__, url_prefix='/meetups')


@module.route('/doc/<docid>')
def view_doc(docid):
    return current_app.view_functions['meetups.meetup'](date=None,
            docid=docid)


@module.route('/')
def meetups():
    """List all meetups in chronological order"""
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=False, startkey=now_key))
            )

@module.route('/<date>')
def meetup(date, docid=None):
    if docid is None:
        doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
                include_docs=True).first()
    else:
        doc = documents.Meetup.get(docid)
        if not doc.next_version:
            return redirect(url_for('meetups.meetup', date=filters.datecode(doc.start)))
    if 'root_id' in doc:
        versions = documents.Version.view('frontend/all_versions',
                endkey=[doc['root_id']], startkey=[doc['root_id'], 'Z'],
                descending=True)
    else:
        versions = []
    return render_template('meetup.html',
            meetup = doc,
            doc=doc,
            versions=versions)

@module.route('/<date>/edit', methods=['GET', 'POST'])
@decorators.login_required
def edit_meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
            include_docs=True).first()
    with utils.DocumentLock(doc.root_id) as lock:
        if doc.next_version:
            return abort(403)
        if request.method == 'POST':
            form = forms.MeetupForm.from_flat(request.form)
            if form.validate({'doc': doc}):
                if 'preview' not in request.form:
                    new_doc = utils.save_edit(doc, form)
                    lock.unlock()
                    return redirect(url_for('meetup',
                        date=filters.datecode(new_doc.start)))
        else:
            form = forms.MeetupForm.from_object(doc)
        return render_template('meetups/edit.html',
                meetup=doc,
                preview='preview' in request.form,
                form=form)

@module.route('/<date>/cancel_edit', methods=['GET', 'POST'])
@decorators.login_required
def cancel_edit_meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
            include_docs=True).first()
    with utils.DocumentLock(doc.root_id) as lock:
        lock.unlock()
    return redirect(url_for('meetup', date=date))

@module.route('/create', methods=['GET','POST'])
@decorators.admin_required
def create_meetup():
    if request.method == 'POST':
        form = forms.MeetupForm.from_flat(request.form)
        if form.validate():
            if 'preview' not in request.form:
                utils.save_new(form, 'meetup')
                return redirect(url_for('meetup',
                    date=filters.datecode(form['start'].value)))
    else:
        form = forms.MeetupForm()
    return render_template('meetups/create.html',
            preview='preview' in request.form,
            form=form)

@module.route('/archive/')
def meetup_archive():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups/archive.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=True, startkey=now_key, include_docs=True))
            )

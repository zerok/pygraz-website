from flask import render_template, Module, request
import datetime
import couchdbkit
from flatland.out.markup import Generator

import pygraz_website as site
from . import documents, forms


root = Module(__name__, url_prefix='')

@root.context_processor
def add_form_generator():
    return {'formgen': Generator(auto_for=True)}

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
def meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date, 
            include_docs=True).first()
    return render_template('meetup.html',
            meetup = doc)

@root.route('/meetups/<date>/edit', methods=['GET', 'POST'])
def edit_meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
            include_docs=True).first()
    if request.method == 'POST':
        form = forms.MeetupForm.from_flat(request.form)
        if form.validate({'doc': doc}):
            print "OK"
        else:
            print "NOK"
    else:
        form = forms.MeetupForm.from_flat(doc)
    return render_template('meetups/edit.html',
            meetup=meetup,
            form=form)


@root.route('/meetups-archive/')
def meetup_archive():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups/archive.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=True, startkey=now_key, include_docs=True))
            )

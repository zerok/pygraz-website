from flask import render_template, Module
import datetime
import couchdbkit

import pygraz_website as site
from . import documents


root = Module(__name__, url_prefix='')

@root.route('/')
def index():
    return render_template('index.html')

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

@root.route('/meetups-archive/')
def meetup_archive():
    now_key = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
    return render_template('meetups/archive.html',
            meetups = list(documents.Meetup.view('frontend/meetups_by_date',
                descending=True, startkey=now_key, include_docs=True))
            )

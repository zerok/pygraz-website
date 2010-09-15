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

@root.route('/meetups/<doc>')
def meetup(doc):
    meetup = site.couchdb[doc]
    return render_template('meetup.html',
            meetup = meetup)

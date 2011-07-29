from flask import Blueprint, request, redirect, abort, render_template,\
        current_app, url_for

import pygraz_website as site
from pygraz_website import decorators, models, db, utils


module = Blueprint('core', __name__)

@module.route('/')
def index():
    news = db.session.query(models.Tweet).order_by(models.Tweet.created_at.desc())[:5]
    next_meetup = db.session.query(models.Meetup).order_by(models.Meetup.start.asc()).filter(models.Meetup.start > utils.utcnow()).first()
    return render_template('index.html', next_meetup=next_meetup,
            news=news)


"""
This blueprint's sole purpose is to render the frontpage. Everything else is
done by application specific modules.
"""
from flask import Blueprint, render_template

from pygraz_website import models, db, utils


module = Blueprint('core', __name__)


@module.route('/')
def index():
    news = db.session.query(models.Tweet).order_by(
            models.Tweet.created_at.desc())[:5]
    next_meetup = db.session.query(models.Meetup)\
            .order_by(models.Meetup.start.asc())\
            .filter(models.Meetup.start > utils.utcnow()).first()
    return render_template('index.html', next_meetup=next_meetup,
            news=news)

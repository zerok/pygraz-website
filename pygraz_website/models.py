from flask import url_for
from sqlalchemy.orm.attributes import instance_dict
from pygraz_website import db, filters
import pytz
import datetime


class Meetup(db.Model):
    id = db.Column(db.Integer, db.Sequence('meetup_id_seq'), primary_key=True)
    start = db.Column(db.DateTime(timezone=False))
    end = db.Column(db.DateTime(timezone=False))
    location = db.Column(db.String(255))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    meetupcom_eventid = db.Column(db.String(255))

    def as_dict(self):
        return instance_dict(self)

    def get_absolute_url(self):
        return url_for('meetups.meetup', date=filters.datecode(self.start))

    @classmethod
    def query_by_date(cls, date):
        utc_date = None
        if date.tzinfo == pytz.UTC:
            utc_date = date
        elif date.tzinfo is None:
            utc_date = pytz.utc.localize(date).astimezone(pytz.UTC)
        else:
            utc_date = date.astimezone(pytz.utc)
        start = utc_date.replace(minute=0, second=0, hour=0, microsecond=0)
        end = utc_date + datetime.timedelta(days=1)
        return db.session.query(cls).filter(cls.start.between(start, end))


class Sessionidea(db.Model):
    id = db.Column(db.Integer, db.Sequence('sessionidea_id_seq'),
            primary_key=True)
    summary = db.Column(db.String(255))
    details = db.Column(db.Text)
    url = db.Column(db.String(1024), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('sessionideas',
        lazy='dynamic', cascade='delete'))
    meetup_id = db.Column(db.Integer, db.ForeignKey('meetup.id'))
    meetup = db.relationship('Meetup', backref=db.backref('sessionideas',
        lazy='dynamic', cascade='delete'))


class SessionideaVote(db.Model):
    id = db.Column(db.Integer, db.Sequence('sessionideavote_id_seq'),
            primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sessionidea_id = db.Column(db.Integer, db.ForeignKey('sessionidea.id'))
    user = db.relationship('User', backref=db.backref('sessionideasVotes',
        lazy='dynamic'))
    sessionIdea = db.relationship('Sessionidea', backref=db.backref('votes',
        lazy='dynamic', cascade='delete'))
    value = db.Column(db.Integer)


class Tweet(db.Model):
    id = db.Column(db.Integer, db.Sequence('tweet_id_seq'), primary_key=True)
    text = db.Column(db.Text)
    external_id = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime(timezone=False))
    in_reply_to_status_id = db.Column(db.String)
    in_reply_to_screen_name = db.Column(db.String)

    @property
    def utc_created_at(self):
        return self.created_at.replace(tzinfo=pytz.utc)

    @property
    def url(self):
        return 'http://twitter.com/pygraz/status/%s' % (
                unicode(self.external_id),)

    @classmethod
    def from_tweet(cls, tweet):
        inst = cls()
        inst.text = tweet.text
        inst.external_id = str(tweet.id)
        inst.created_at = tweet.created_at
        inst.in_reply_to_status_id = tweet.in_reply_to_status_id
        inst.in_reply_to_screen_name = tweet.in_reply_to_screen_name
        return inst


class User(db.Model):
    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email_status = db.Column(db.String, nullable=True, default="not_verified")
    email_activation_code = db.Column(db.String, nullable=True)
    email_notify_new_meetup = db.Column(db.Boolean, nullable=True, default=False)
    email_notify_new_sessionidea = db.Column(db.Boolean, nullable=True, default=False)

    def email_activated(self):
        return self.email_status in ("active",)


class OpenID(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('openids',
        lazy='dynamic', cascade='delete'))

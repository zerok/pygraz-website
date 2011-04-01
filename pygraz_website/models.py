from sqlalchemy.orm.attributes import instance_dict
from pygraz_website import db
import pytz, datetime


class Meetup(db.Model):
    id = db.Column(db.Integer, db.Sequence('meetup_id_seq'), primary_key=True)
    start = db.Column(db.DateTime(timezone=True))
    end = db.Column(db.DateTime(timezone=True))
    location = db.Column(db.String(255))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)

    def as_dict(self):
        return instance_dict(self)

    @classmethod
    def query_by_date(cls, date):
        utc_date = None
        if date.tzinfo == pytz.UTC:
            utc_date = date
        else:
            utc_date = date.astimezone(pytz.UTC)
        start = utc_date.replace(minute=0, second=0, hour=0, microsecond=0)
        end = utc_date + datetime.timedelta(days=1)
        return db.session.query(cls).filter(cls.start.between(start, end))

class Tweet(db.Model):
    id = db.Column(db.Integer, db.Sequence('meetup_id_seq'), primary_key=True)
    text = db.Column(db.Text)
    external_id = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime(timezone=True))
    in_reply_to_status_id = db.Column(db.String)
    in_reply_to_screen_name = db.Column(db.String)

    @property
    def utc_created_at(self):
        return self.created_at.replace(tzinfo=pytz.utc)

    @property
    def url(self):
        return 'http://twitter.com/pygraz/status/%s' % (unicode(self.external_id),)

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

class OpenID(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('openids', lazy='dynamic'))

user_role = db.Table('user_role', 
        db.Column('user_id', db.ForeignKey('user.id')),
        db.Column('role_id', db.ForeignKey('role.id'))
        )

class Role(db.Model):
    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key=True)
    name = db.Column(db.String, unique=True)
    users = db.relationship('User', secondary=user_role,
            backref=db.backref('roles', lazy='dynamic'))


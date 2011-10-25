from sqlalchemy import *
from migrate import *


meta = MetaData()


meetup = Table('meetup', meta,
    Column('id', Integer, Sequence('meetup_id_seq'), primary_key=True),
    Column('start', DateTime(timezone=False)),
    Column('end', DateTime(timezone=False)),
    Column('location', String(255)),
    Column('address', String(255)),
    Column('notes', Text)
    )

tweet = Table(
    'tweet', meta,
    Column('id', Integer, Sequence('tweet_id_seq'), primary_key=True),
    Column('text', Text),
    Column('external_id', String, unique=True),
    Column('created_at', DateTime(timezone=False)),
    Column('in_reply_to_status_id', String),
    Column('in_reply_to_screen_name', String)
    )

sessionidea = Table('sessionidea', meta,
    Column('id', Integer, Sequence('sessionidea_id_seq'), primary_key=True),
    Column('summary', String(255)),
    Column('details', Text),
    Column('url', String(1024), nullable=True),
    Column('author_id', Integer, ForeignKey('user.id')),
    Column('meetup_id', Integer, ForeignKey('meetup.id'))
    )

sessionidea_vote = Table('sessionidea_vote', meta,
    Column('id', Integer, Sequence('sessionideavote_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('sessionidea_id', Integer, ForeignKey('sessionidea.id')),
    Column('value', Integer)
    )

user = Table(
    'user', meta,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('username', String, unique=True),
    Column('email', String),
    Column('is_admin', Boolean, nullable=True, default=False)
    )

openid = Table(
    'openID', meta,
    Column('id', String, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'))
    )


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user.create()
    openid.create()
    meetup.create()
    sessionidea.create()
    tweet.create()
    sessionidea_vote.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    sessionidea_vote.drop()
    tweet.drop()
    sessionidea.drop()
    meetup.drop()
    openid.drop()
    user.drop()

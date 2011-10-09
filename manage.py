from flaskext.script import Manager
import pygraz_website
from pygraz_website import models, db
import tweepy
import settings

app = pygraz_website.create_app(config_object=settings)


manager = Manager(app)


@manager.option("--dry-run", dest='dryrun', action='store_true')
@manager.command
def sync_twitter(dryrun=False):
    last_tweet = models.Tweet.query\
            .order_by(models.Tweet.created_at.desc()).first()
    last_id = None
    if last_tweet:
        print "Last ID: " + str(last_tweet.external_id)
        last_id = last_tweet.external_id
    for tweet in tweepy.Cursor(tweepy.api.user_timeline, 'pygraz',
            since_id=last_id).items(100):
        if dryrun:
            print tweet.id
        else:
            db.session.add(models.Tweet.from_tweet(tweet))
            db.session.commit()


@manager.command
def create_db():
    db.create_all()


@manager.command
def runserver():
    app.run()


@manager.option('--make-admin', dest='make_admin', action='store')
@manager.command
def update_user(openid, make_admin=None):
    user = db.session.query(models.OpenID)\
            .filter(models.OpenID.id == openid)\
            .first().user
    print user
    if make_admin == '1':
        user.is_admin = True
    elif make_admin == '0':
        user.is_admin = False
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()

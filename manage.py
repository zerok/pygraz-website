from flaskext.script import Manager
import pygraz_website as site
from pygraz_website import models
import tweepy
from os.path import join, dirname, abspath
from couchdbkit.loaders import FileSystemDocsLoader


manager = Manager(site.app)

@manager.option("--dry-run", dest='dryrun', action='store_true')
@manager.command
def sync_twitter(dryrun=False):
    last_tweet = models.Tweet.query.order_by(models.Tweet.created_at.desc()).first()
    last_id = None
    if last_tweet:
        print "Last ID: " + str(last_tweet.external_id)
        last_id = last_tweet.external_id
    for tweet in tweepy.Cursor(tweepy.api.user_timeline, 'pygraz', since_id=last_id).items(100):
        if dryrun:
            print tweet.id
        else:
            site.db.session.add(models.Tweet.from_tweet(tweet))
            site.db.session.commit()

@manager.command
def load_designdocs():
    docs_path = join(abspath(dirname(__file__)), '_design')
    loader = FileSystemDocsLoader(docs_path)
    loader.sync(site.couchdb, verbose=True)

@manager.command
def create_db():
    site.db.create_all()

@manager.command
def runserver():
    site.app.run()

manager.run()

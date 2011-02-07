from flaskext.script import Manager
import pygraz_website as site
from pygraz_website import documents
import tweepy
from os.path import join, dirname, abspath
from couchdbkit.loaders import FileSystemDocsLoader


app = site.create_app('FLASK_SETTINGS')
site.load_db(app)

manager = Manager(app)

@manager.option("--dry-run", dest='dryrun', action='store_true')
@manager.command
def sync_twitter(dryrun=False):
    keyrow = site.couchdb.view('admin/twitter_external_ids').first()
    ids = set()
    if keyrow:
        ids = set(keyrow['value'])
    last_update = documents.Tweet.view('frontend/tweet_by_external_id', limit=1, descending=True).first()
    last_id = last_update is not None and last_update.external_id or None
    print "Last ID: " + str(last_id)
    for tweet in tweepy.Cursor(tweepy.api.user_timeline, 'pygraz', since_id=last_id).items(100):
        if tweet.id not in ids:
            if dryrun:
                print tweet.id
            else:
                documents.Tweet.from_tweet(tweet).save()

@manager.command
def load_designdocs():
    docs_path = join(abspath(dirname(__file__)), '_design')
    loader = FileSystemDocsLoader(docs_path)
    loader.sync(site.couchdb, verbose=True)

manager.run()

from flaskext.script import Manager
import pygraz_website as site
from pygraz_website import documents
import tweepy


app = site.create_app('FLASK_SETTINGS')
site.load_db(app)

manager = Manager(app)

@manager.option("--dry-run", dest='dryrun', action='store_true')
@manager.command
def sync_twitter(dryrun=False):
    last_update = documents.Tweet.view('frontend/tweet_by_external_id', limit=1, descending=True).first()
    last_id = last_update is not None and last_update.external_id or None
    for tweet in tweepy.Cursor(tweepy.api.user_timeline, 'pygraz', since_id=last_id).items(100):
        if dryrun:
            print tweet.id
        else:
            documents.Tweet.from_tweet(tweet).save()

manager.run()

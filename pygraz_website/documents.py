import couchdbkit
import pytz


class Version(couchdbkit.Document):
    updated_at = couchdbkit.DateTimeProperty()
    next_version = couchdbkit.StringProperty()
    previous_version = couchdbkit.StringProperty()
    root_id = couchdbkit.StringProperty()

class Meetup(Version):
    doc_type = 'meetup'
    start = couchdbkit.DateTimeProperty()
    end = couchdbkit.DateTimeProperty()
    location = couchdbkit.DictProperty()
    notes = couchdbkit.StringProperty()

    @property
    def utc_start(self):
        return self.start.replace(tzinfo=pytz.utc)

    @property
    def utc_end(self):
        return self.end.replace(tzinfo=pytz.utc)

class User(couchdbkit.Document):
    doc_type = 'user'
    username = couchdbkit.StringProperty()
    email = couchdbkit.StringProperty()
    openids = couchdbkit.ListProperty()
    roles = couchdbkit.ListProperty(default=[])

class Tweet(couchdbkit.Document):
    doc_type = 'tweet'
    text = couchdbkit.StringProperty()
    external_id = couchdbkit.IntegerProperty()
    created_at = couchdbkit.DateTimeProperty()
    in_reply_to_status_id = couchdbkit.StringProperty()
    in_reply_to_screen_name = couchdbkit.StringProperty()
    @property
    def utc_created_at(self):
        return self.created_at.replace(tzinfo=pytz.utc)

    @property
    def url(self):
        return 'http://twitter.com/pygraz/status/%d' % (self.external_id,)

    @classmethod
    def from_tweet(cls, tweet):
        inst = cls()
        inst.text = tweet.text
        inst.external_id = tweet.id
        inst.created_at = tweet.created_at
        inst.in_reply_to_status_id = tweet.in_reply_to_status_id
        inst.in_reply_to_screen_name = tweet.in_reply_to_screen_name
        print inst
        return inst

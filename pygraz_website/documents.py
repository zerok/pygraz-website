import couchdbkit
import pytz


class Version(couchdbkit.Document):
    updated_at = couchdbkit.DateTimeProperty()
    next_version = couchdbkit.StringProperty()
    previous_version = couchdbkit.StringProperty()
    root_id = couchdbkit.StringProperty()

class Meetup(Version):
    _doc_type = 'meetup'
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
    _doc_type = 'user'
    name = couchdbkit.StringProperty()
    email = couchdbkit.StringProperty()
    openids = couchdbkit.ListProperty()
    roles = couchdbkit.ListProperty(default=[])

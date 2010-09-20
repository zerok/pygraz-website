import couchdbkit

class Version(couchdbkit.Document):
    updated_at = couchdbkit.DateTimeProperty()
    next_version = couchdbkit.StringProperty()
    previous_version = couchdbkit.StringProperty()
    root_id = couchdbkit.StringProperty()

class Meetup(Version):
    start = couchdbkit.DateTimeProperty()
    end = couchdbkit.DateTimeProperty()
    location = couchdbkit.DictProperty()
    notes = couchdbkit.StringProperty()

class User(couchdbkit.Document):
    name = couchdbkit.StringProperty()
    email = couchdbkit.StringProperty()
    openids = couchdbkit.ListProperty()
    roles = couchdbkit.ListProperty()

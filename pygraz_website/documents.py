import couchdbkit

class Meetup(couchdbkit.Document):
    start = couchdbkit.DateTimeProperty()
    end = couchdbkit.DateTimeProperty()
    location = couchdbkit.DictProperty()
    notes = couchdbkit.StringProperty()
    updated_at = couchdbkit.DateTimeProperty()

class Version(couchdbkit.Document):
    updated_at = couchdbkit.DateTimeProperty()
    next_version = couchdbkit.StringProperty()
    previous_version = couchdbkit.StringProperty()
    root_id = couchdbkit.StringProperty()

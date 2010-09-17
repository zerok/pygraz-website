import couchdbkit

class Meetup(couchdbkit.Document):
    start = couchdbkit.DateTimeProperty()
    end = couchdbkit.DateTimeProperty()
    location = couchdbkit.DictProperty()
    notes = couchdbkit.StringProperty()

import flatland
from flatland.validation import Present, Validator, IsEmail
from flatland.validation.base import N_
from flatland.out.markup import Generator
import pytz
import __builtin__
from flask import current_app

from pygraz_website import filters
import pygraz_website as site
from pygraz_website.documents import Meetup


class LocalDateTime(flatland.DateTime):
    def adapt(self, value):
        local_tz = current_app.config['local_timezone']
        if isinstance(value, self.type_):
            return flatland.DateTime.adapt(self,
                    pytz.utc.localize(value).astimezone(local_tz))
        else:
            # We are in "store" mode, so a string is coming from the form
            result = flatland.DateTime.adapt(self, value)
            return local_tz.localize(result).astimezone(pytz.utc)

class DateAfterOther(Validator):
    fail = "%(label)s has to be after %(othervalue)s"

    def __init__(self, othername):
        self.othername = othername
        Validator.__init__(self)

    def validate(self, element, state):
        other = element.parent.el(self.othername)
        if other.value is None:
            return None
        if element.value is None or element.value < other.value:
            self.note_error(element, state, 'fail', othervalue=other.value)
            return False
        return True

class UniqueMeetupStartDate(Validator):
    fail = "Am selben Tag findet schon ein Treffen statt."

    def validate(self, element, state):
        docs = Meetup.view('frontend/meetups_by_date',
                key=filters.datecode(element.value))
        if state is not None:
            for d in docs:
                if d['_id'] != state['doc']['_id']:
                    self.note_error(element, state, 'fail')
                    return False
        else:
            if docs.count() > 0:
                self.note_error(element, state, 'fail')
                return False
        return True

class UniqueUsername(Validator):
    fail = "Dieser Benutzername wird schon von jemand anderem verwendet."

    def validate(self, element, state):
        res = site.couchdb.view('frontend/users_by_username', key=element.u.rstrip().lstrip())
        if res.count() != 0:
            self.note_error(element, state, 'fail')
            return False
        return True

class MeetupForm(flatland.Form):
    start = LocalDateTime.using(name="start", validators=[
        Present(), UniqueMeetupStartDate()])
    end = LocalDateTime.using(name="end", validators=[
        Present(), DateAfterOther('start')])
    notes = flatland.String.using(optional=True)
    location = flatland.Dict.of(
        flatland.String.named('name'),
        flatland.String.named('address').using(optional=True)
        )

class LoginForm(flatland.Form):
    openid = flatland.String.using(name='openid', validators=[
        Present()
        ])

class RegisterForm(flatland.Form):
    username = flatland.String.using(name="username", validators=[
        Present(), UniqueUsername()
        ])
    email = flatland.String.using(name="email", validators=[
        Present(), IsEmail()
        ])

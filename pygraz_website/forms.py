import flatland
from flatland.validation import Present, Validator, IsEmail
from flatland.validation.base import N_
from flatland.out.markup import Generator
import pytz
import __builtin__
from flask import current_app, g

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


class UniqueUserField(Validator):

    def validate(self, element, state):
        res = site.couchdb.view(self.view, key=element.u.rstrip().lstrip())
        for doc in res:
            if g.user is not None and g.user['_id'] == doc['value']['_id']:
                break
            self.note_error(element, state, 'fail')
            return False
        return True

class UniqueUsername(UniqueUserField):
    fail = "Dieser Benutzername wird schon von jemand anderem verwendet."
    view = 'frontend/users_by_username'

class UniqueEmail(UniqueUserField):
    fail = "Diese E-Mail-Adresse wird bereits von jemand anderem verwendet."
    view = 'frontend/users_by_email'

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
        Present(), IsEmail(), UniqueEmail()
        ])

class EditProfileForm(RegisterForm):
    pass

class CompanyForm(flatland.Form):
    name = flatland.String.using(validators=[Present()])
    url = flatland.String
    location = flatland.Dict.of(
        flatland.String.named('address').using(optional=True)
        )

class AdminCompanyForm(CompanyForm):
    confirmed = flatland.Boolean(validators=[Present()])

def get_companyform():
    if 'admin' in getattr(getattr(g, 'user'), 'roles', []):
        return AdminCompanyForm
    return CompanyForm

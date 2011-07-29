import flatland
from flatland.validation import Present, Validator, IsEmail, Converted, LengthBetween
from flatland.validation.base import N_
from flatland.out.markup import Generator
import pytz
import __builtin__
from flask import current_app, g

from pygraz_website import filters
import pygraz_website as site
from pygraz_website import models


class LocalDateTime(flatland.DateTime):
    def adapt(self, value):
        local_tz = current_app.config['local_timezone']
        if isinstance(value, self.type_):
            adapted = flatland.DateTime.adapt(self, value)
            return adapted
        else:
            # We are in "store" mode, so a string is coming from the form
            result = flatland.DateTime.adapt(self, value)
            return local_tz.localize(result).astimezone(pytz.utc).replace(tzinfo=None)

    def serialize(self, value):
        local_tz = current_app.config['local_timezone']
        return super(LocalDateTime, self).serialize(pytz.utc.localize(value).astimezone(local_tz))

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
        if element.value is None:
            return False
        other_meetups = models.Meetup.query_by_date(element.value).all()
        if state is not None:
            for d in other_meetups:
                if d.id != state['meetup'].id:
                    self.note_error(element, state, 'fail')
                    return False
        else:
            if other_meetups:
                self.note_error(element, state, 'fail')
                return False
        return True


class UniqueUserField(Validator):

    def validate(self, element, state):
        users = self.find_users(element)
        for user in users:
            if g.user is not None and g.user.id == user.id:
                break
            self.note_error(element, state, 'fail')
            return False
        return True

class UniqueUsername(UniqueUserField):
    fail = "Dieser Benutzername wird schon von jemand anderem verwendet."

    def find_users(self, element):
        return models.User.query.filter(models.User.username==element.u.rstrip().lstrip())

class UniqueEmail(UniqueUserField):
    fail = "Diese E-Mail-Adresse wird bereits von jemand anderem verwendet."

    def find_users(self, element):
        return models.User.query.filter(models.User.email==element.u.rstrip().lstrip())

class MeetupForm(flatland.Form):
    start = LocalDateTime.using(name="start", validators=[
        Present(), Converted(), UniqueMeetupStartDate()])
    end = LocalDateTime.using(name="end", validators=[
        Present(), Converted(), DateAfterOther('start')])
    notes = flatland.String.using(optional=True)
    location = flatland.String.using(optional=True)
    address = flatland.String.using(optional=True)

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

class SessionIdeaForm(flatland.Form):
    summary = flatland.String.using(validators=[Present(), LengthBetween(1, 255)])
    details = flatland.String.using(validators=[Present()])
    url = flatland.String.using(optional=True)


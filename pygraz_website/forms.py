#-*- encoding: utf-8 -*-
import flatland
from flatland.validation import Present, Validator, IsEmail, Converted,\
        LengthBetween
import pytz
from flask import current_app, g
from flaskext.babel import lazy_gettext as _

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
            return local_tz.localize(result).astimezone(pytz.utc)\
                    .replace(tzinfo=None)

    def serialize(self, value):
        local_tz = current_app.config['local_timezone']
        return super(LocalDateTime, self).serialize(
                pytz.utc.localize(value).astimezone(local_tz))


class DateAfterOther(Validator):
    fail = "%(label)s has to be after %(othervalue)s"

    def __init__(self, othername, *args, **kwargs):
        self.othername = othername
        Validator.__init__(self, *args, **kwargs)

    def validate(self, element, state):
        other = element.parent.el(self.othername)
        if other.value is None:
            return None
        if element.value is None or element.value < other.value:
            self.note_error(element, state, 'fail', othervalue=other.value)
            return False
        return True


class UniqueMeetupStartDate(Validator):
    fail = _('There already is a meetup on this day')

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
    fail = _('This username is already taken')

    def find_users(self, element):
        return models.User.query.filter(
                models.User.username == element.u.rstrip().lstrip())


class UniqueEmail(UniqueUserField):
    fail = _('This email address is already taken')

    def find_users(self, element):
        return models.User.query.filter(
                models.User.email == element.u.rstrip().lstrip())


class MeetupForm(flatland.Form):
    start = LocalDateTime.using(name="start", validators=[
            Present(missing=_('Please provide a start datetime')),
            Converted(),
            UniqueMeetupStartDate()])
    end = LocalDateTime.using(name="end", validators=[
            Present(missing=_('Please provide an end datetime')),
            Converted(),
            DateAfterOther('start',
                fail=_('The end has to come after the start'))])
    notes = flatland.String.using(optional=True)
    location = flatland.String.using(optional=True)
    address = flatland.String.using(optional=True)


class LoginForm(flatland.Form):
    openid = flatland.String.using(name='openid', validators=[
            Present(missing=_('Please provide an OpenID in order to login'))])


class RegisterForm(flatland.Form):
    username = flatland.String.using(name="username", validators=[
            Present(missing=_('Please provide a username')),
            UniqueUsername()])
    email = flatland.String.using(name="email", validators=[
            Present(missing=_('Please provide an email address')),
            IsEmail(invalid=_('Please provide a valid email address')),
            UniqueEmail()])


class EditProfileForm(RegisterForm):
    pass


class SessionIdeaForm(flatland.Form):
    summary = flatland.String.using(validators=[
            Present(missing=_('Please give your idea a summary')),
            LengthBetween(1, 255,
                breached=_('The summary of your idea has to be between 1 and 255 chars long'))])
    details = flatland.String.using(validators=[
            Present(missing=_('Please describe your idea'))])
    url = flatland.String.using(optional=True)

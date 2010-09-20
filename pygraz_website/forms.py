import flatland
from flatland.validation import Present, Validator, IsEmail
from flatland.validation.base import N_
from flatland.out.markup import Generator
import __builtin__

from pygraz_website import filters


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
        docs = state['doc'].__class__.view('frontend/meetups_by_date',
                key=filters.datecode(element.value))
        for d in docs:
            if d['_id'] != state['doc']['_id']:
                self.note_error(element, state, 'fail')
                return False
        return True

class MeetupForm(flatland.Form):
    start = flatland.DateTime.using(name="start", validators=[
        Present(), UniqueMeetupStartDate()])
    end = flatland.DateTime.using(name="end", validators=[
        Present(), DateAfterOther('start')])
    notes = flatland.String.using(optional=True)

class LoginForm(flatland.Form):
    openid = flatland.String.using(name='openid', validators=[
        Present()
        ])

class RegisterForm(flatland.Form):
    username = flatland.String.using(name="username", validators=[
        Present()
        ])
    email = flatland.String.using(name="email", validators=[
        Present(), IsEmail()
        ])

import flatland
from flatland.validation import Present, Validator, IsEmail
from flatland.validation.base import N_
from flatland.out.markup import Generator
import __builtin__


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

def meetup_unique_start_date(elem, state):
    return True

class MeetupForm(flatland.Form):
    start = flatland.DateTime.using(name="start", validators=[
        Present(), meetup_unique_start_date])
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

from flask import session, g
from . import documents


def check_user():
    if 'openid' in session:
        g.user = documents.User.view('frontend/users_by_openid',
                key=session['openid']).first()

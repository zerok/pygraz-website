from flask import session, g, current_app
from . import documents


def check_user():
    if 'FAKE_LOGIN' in current_app.config and 'openid' not in session:
        session['openid'] = current_app.config['FAKE_LOGIN']
    if 'openid' in session:
        g.user = documents.User.view('frontend/users_by_openid',
                key=session['openid']).first()
    else:
        g.user = None

from flask import session, g, current_app
from . import db, models


def check_user():
    """
    Handle login information and also allow for a fake login to be made
    during initial development.
    """
    if 'FAKE_LOGIN' in current_app.config and 'openid' not in session:
        session['openid'] = current_app.config['FAKE_LOGIN']
    if 'openid' in session:
        g.user = db.session.query(models.User).join(models.OpenID).filter(models.OpenID.id==session['openid']).first()
    else:
        g.user = None

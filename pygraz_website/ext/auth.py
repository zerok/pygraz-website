from flask import g, session


class Auth(object):
    """
    This is just a simple app extension to handle basic authentication as
    used by this specific application.
    """

    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.context_processor(self.auth_processor)
        app.before_request(self.before_request)
        self.app = app

    def auth_processor(self):
        """
        Inject some simple account status flags into each page.
        """
        result = {
                'is_logged_in': False,
                'is_admin': False}
        if hasattr(g, 'user') and g.user is not None:
            result['is_logged_in'] = True
            result['is_admin'] = g.user.is_admin
        return result

    def before_request(self):
        """
        Handle login information and also allow for a fake login to be made
        during initial development.
        """
        from .. import db, models

        if 'FAKE_LOGIN' in self.app.config and 'openid' not in session:
            session['openid'] = self.app.config['FAKE_LOGIN']
        if 'openid' in session:
            g.user = db.session.query(models.User)\
                    .join(models.OpenID)\
                    .filter(models.OpenID.id == session['openid']).first()
        else:
            g.user = None

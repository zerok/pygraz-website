from flask import Flask
from flask.ext.babel import Babel, get_translations
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.redis import Redis
from flask.ext.compass import Compass
from . import filters, context_processors, utils, ext
import __builtin__
import pytz
import logging.handlers


redis = Redis()
db = SQLAlchemy()
auth = ext.Auth()
compass = Compass()
oid = OpenID()
babel = Babel()


def create_app(envar="FLASK_SETTINGS", config_object=None):
    app = Flask(__name__)
    if config_object is None:
        app.config.from_envvar("FLASK_SETTINGS")
    else:
        app.config.from_object(config_object)
    if 'local_timezone' not in app.config:
        app.config['local_timezone'] = pytz.timezone('Europe/Vienna')
    if 'type2module' not in app.config:
        app.config['type2view'] = {
                'meetup': 'meetups.view_doc',
                'company': 'companies.view_doc',
                }
    if 'LOG_FILE' in app.config:
        handler = logging.handlers.RotatingFileHandler(app.config['LOG_FILE'],
                backupCount=5, maxBytes=1000000)
        if 'LOG_LEVEL' in app.config:
            handler.setLevel(app.config['LOG_LEVEL'])
        else:
            handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    app.jinja_env.filters['time'] = filters.timefilter
    app.jinja_env.filters['date'] = filters.datefilter
    app.jinja_env.filters['datecode'] = filters.datecode
    app.jinja_env.filters['datetime'] = filters.datetimefilter
    app.jinja_env.filters['rst'] = filters.rst
    app.jinja_env.filters['urlencode'] = filters.urlencode
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    auth.init_app(app)
    compass.init_app(app)

    from . import models

    # Register modules
    from .views.account import module as account_module
    from .views.admin import module as admin_module
    from .views.core import module as core_module
    from .views.meetups import module as meetups_module
    app.register_blueprint(core_module, url_prefix='')
    app.register_blueprint(account_module, url_prefix='/account')
    app.register_blueprint(admin_module, url_prefix='/admin')
    app.register_blueprint(meetups_module, url_prefix='/meetups')

    #Register context and request processors
    app.context_processor(context_processors.add_form_generator)

    # Register babel's i18n functions globally in order for Flatland to see
    # them.
    babel.init_app(app)
    oid.init_app(app)
    __builtin__.ugettext = lambda x: get_translations().ugettext(x)
    __builtin__.ungettext = lambda x,s,p: get_translations().ungettext(x,s,p)
    app.error_handlers[409] = utils.handle_conflict
    redis.init_app(app)

    return app

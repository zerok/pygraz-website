from flask import Flask
from flaskext.babel import Babel, get_translations
from flaskext.openid import OpenID
import couchdbkit
from . import documents, filters, context_processors, request_processors, utils
import __builtin__
import redis as redisapi
import pytz

couchdb = None
babel = None
redis = None
oid = OpenID()

def create_app(settings):
    global babel, oid
    app = Flask(__name__)
    app.config.from_envvar(settings)
    if 'local_timezone' not in app.config:
        app.config['local_timezone'] = pytz.timezone('Europe/Vienna')
    if 'type2module' not in app.config:
        app.config['type2view'] = {
                'meetup': 'meetups.view_doc',
                }

    app.jinja_env.filters['time'] = filters.timefilter
    app.jinja_env.filters['date'] = filters.datefilter
    app.jinja_env.filters['datecode'] = filters.datecode
    app.jinja_env.filters['datetime'] = filters.datetimefilter
    app.jinja_env.filters['rst'] = filters.rst
    app.secret_key = app.config['SECRET_KEY']


    from .views.account import module as account_module
    from .views.core import module as core_module
    from .views.meetups import module as meetups_module
    app.register_module(core_module)
    app.register_module(account_module)
    app.register_module(meetups_module)
    app.context_processor(context_processors.add_form_generator)
    app.context_processor(context_processors.auth_processor)
    app.before_request(request_processors.check_user)
    babel = Babel(app)
    oid.init_app(app)

    # Register babel's i18n functions globally in order for Flatland to see
    # them.
    __builtin__.ugettext = lambda x : get_translations().ugettext(x)
    __builtin__.ungettext = lambda x,s,p: get_translations().ungettext(x,s,p)
    app.error_handlers[409] = utils.handle_conflict
    return app


def load_db(app):
    """
    Initializes the connection pool
    """
    global couchdb, redis
    if couchdb is not None:
        app.log.warn("couchdb already initialzed")
        return
    server = couchdbkit.Server(app.config['COUCHDB_SERVER'])
    couchdb = server.get_or_create_db(app.config['COUCHDB_DATABASE'])
    couchdbkit.Document.set_db(couchdb)
    documents.Version.set_db(couchdb)
    documents.Meetup.set_db(couchdb)

    redis = redisapi.Redis(app.config.get('REDIS_HOST', 'localhost'),
            app.config.get('REDIS_HOST', 6379),
            app.config.get('REDIS_DB', 0))


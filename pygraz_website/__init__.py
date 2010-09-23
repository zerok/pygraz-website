from flask import Flask
from flaskext.babel import Babel, get_translations
from flaskext.openid import OpenID
import couchdbkit
from . import documents, filters
import __builtin__
import redis as redisapi

couchdb = None
babel = None
redis = None
oid = OpenID()

def create_app(settings):
    global babel, oid
    app = Flask(__name__)
    app.config.from_envvar(settings)

    app.jinja_env.filters['time'] = filters.timefilter
    app.jinja_env.filters['date'] = filters.datefilter
    app.jinja_env.filters['datecode'] = filters.datecode
    app.jinja_env.filters['rst'] = filters.rst
    app.secret_key = app.config['SECRET_KEY']


    from .views import root, handle_conflict
    app.register_module(root)
    babel = Babel(app)
    oid.init_app(app)

    # Register babel's i18n functions globally in order for Flatland to see
    # them.
    __builtin__.ugettext = lambda x : get_translations().ugettext(x)
    __builtin__.ungettext = lambda x,s,p: get_translations().ungettext(x,s,p)
    app.error_handlers[409] = handle_conflict
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


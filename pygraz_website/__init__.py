from flask import Flask
from flaskext.babel import Babel, get_translations
import couchdbkit
from . import documents, filters
import __builtin__

couchdb = None
babel = None

def create_app(settings):
    global babel
    app = Flask(__name__)
    app.config.from_envvar(settings)

    app.jinja_env.filters['time'] = filters.timefilter
    app.jinja_env.filters['date'] = filters.datefilter
    app.jinja_env.filters['datecode'] = filters.datecode
    app.jinja_env.filters['rst'] = filters.rst

    from .views import root
    app.register_module(root)
    babel = Babel(app)

    # Register babel's i18n functions globally in order for Flatland to see
    # them.
    __builtin__.ugettext = lambda x : get_translations().ugettext(x)
    __builtin__.ungettext = lambda x,s,p: get_translations().ungettext(x,s,p)
    return app


def load_db(app):
    """
    Initializes the connection pool
    """
    global couchdb
    if couchdb is not None:
        app.log.warn("couchdb already initialzed")
        return
    server = couchdbkit.Server(app.config['COUCHDB_SERVER'])
    couchdb = server.get_or_create_db(app.config['COUCHDB_DATABASE'])
    couchdbkit.Document.set_db(couchdb)
    documents.Meetup.set_db(couchdb)



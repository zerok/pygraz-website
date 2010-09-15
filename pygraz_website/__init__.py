from flask import Flask
import couchdbkit
from . import documents, filters

couchdb = None

def create_app(settings):
    app = Flask(__name__)
    app.config.from_envvar(settings)

    app.jinja_env.filters['time'] = filters.timefilter
    app.jinja_env.filters['date'] = filters.datefilter

    from .views import root
    app.register_module(root)
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



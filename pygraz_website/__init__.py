from flask import Flask
from flaskext.babel import Babel, get_translations
from flaskext.openid import OpenID
from flaskext.sqlalchemy import SQLAlchemy
from . import filters, context_processors, utils
import __builtin__
import redis as redisapi
import pytz
import logging.handlers


couchdb = None
babel = None
redis = None
db = None
oid = OpenID()

app = Flask(__name__)
app.config.from_envvar("FLASK_SETTINGS")
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

db = SQLAlchemy(app)
from . import models

# Register modules
from .views.account import module as account_module
from .views.admin import module as admin_module
from .views.core import module as core_module
from .views.meetups import module as meetups_module
for k, v in locals().items():
    if k.endswith('_module'):
        app.register_module(v)

#Register context and request processors
app.context_processor(context_processors.add_form_generator)
app.context_processor(context_processors.auth_processor)
from . import request_processors
app.before_request(request_processors.check_user)

# Register babel's i18n functions globally in order for Flatland to see
# them.
babel = Babel(app)
oid.init_app(app)
__builtin__.ugettext = lambda x : get_translations().ugettext(x)
__builtin__.ungettext = lambda x,s,p: get_translations().ungettext(x,s,p)
app.error_handlers[409] = utils.handle_conflict


# Init Redis for handling of locks
redis = redisapi.Redis(app.config.get('REDIS_HOST', 'localhost'),
        app.config.get('REDIS_PORT', 6379),
        app.config.get('REDIS_DB', 0))


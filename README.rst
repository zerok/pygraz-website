pyGRAZ-Website
##############

Local installation
==================

For a local installation you require besides those components mentioned in the
requirements.txt following software:

* redis (for Wiki locks)
* postgresql (as primary data store)
* compass (for compiling the stylesheets)

You also have to provide a settings module (e.g. settings.py) with following
settings (replace the dummy values if necessary)::
    
    from os.path import dirname, abspath, join
    HERE = dirname(abspath(__file__))
    SQLALCHEMY_DATABASE_URI='postgres://localhost/pygraz'
    DEBUG=True
    SECRET_KEY = "test"
    LOG_FILE='development.log'
    COMPASS_CONFIGS = [join(HERE, 'pygraz_website/static/s/config.rb')]

    import locale
    locale.setlocale(locale.LC_ALL, "de_AT.utf8")

Ideally the settings.py should be stored in the same directory as the
runserver.py and setenv.sh.

Once you have your configuration file in place, it's time to tell flask where
to find it::
    
    source env.sh

One last step before pygraz_website is ready to go: Initializing the database.
For this you first have to create a database with the name you specified in
the settings.py on your server. The necessary database tables can be created
by running following command::
    
    python manage.py create_db

Now you should be good to go::
    
    python manage.py runserver

Note that when you create a new user account via OpenID now, it won't be an
admin user, so you won't be able to create new meetups among other things. To
make a user admin, set its user's is_admin property to True.


Configuration settings
======================

======================= =============
Setting                 Default value
======================= =============
REDIS_HOST              localhost
REDIS_PORT              6379
REDIS_DB                0
SQLALCHEMY_DATABASE_URI None
LOG_FILE                None
======================= =============

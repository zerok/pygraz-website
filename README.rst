pyGRAZ-Website
##############

Local installation
==================

For a local installation you require besides those components mentioned in the
requirements.txt following software:

* redis (for Wiki locks)
* couchdb (as primary data store)

You also have to provide a settings module (e.g. settings.py) with following
settings (replace the dummy values if necessary)::
    
    COUCHDB_SERVER="http://localhost:5985"
    COUCHDB_DATABASE="pygraz"
    DEBUG=True
    SECRET_KEY = "test"
    LOG_FILE='development.log'

    import locale
    locale.setlocale(locale.LC_ALL, "de_AT.utf8")

Ideally the settings.py should be stored in the same directory as the
runserver.py and setenv.sh.

Once you have your configuration file in place, it's time to tell flask where
to find it::
    
    source env.sh

One last step before pygraz_website is ready to go: Initializing the database.
For this you first have to create a database with the name you specified in
the settings.py on your couchdb server. Once this is done, you have to load
the design docs::
    
    python manage.py load_designdocs

Now you should be good to go::
    
    python runserver.py

Note that when you create a new user account via OpenID now, it won't be an
admin user, so you won't be able to create new meetups among other things. To
make a user admin, give it a new property "roles" with ["admin"] as value.


Configuration settings
======================

================ =============
Setting          Default value
================ =============
REDIS_HOST       localhost
REDIS_PORT       6379
REDIS_DB         0
COUCHDB_SERVER   None
COUCHDB_DATABASE None
LOG_FILE         None
================ =============

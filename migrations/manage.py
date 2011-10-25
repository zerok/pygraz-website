#!/usr/bin/env python
import sys
from os.path import dirname, abspath
from migrate.versioning.shell import main

here = dirname(abspath(__file__))
sys.path.insert(0, dirname(here))

import pygraz_website
import settings


app = pygraz_website.create_app(config_object=settings)


main(debug='False', url=app.config['SQLALCHEMY_DATABASE_URI'],
        repository=here)

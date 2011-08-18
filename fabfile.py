from fabric.api import local
from fabric.context_managers import lcd
from os.path import join, dirname

here = dirname(__file__)

def upload():
    with lcd(here):
        local('epio upload -a pygraz')

def extract_messages():
    with lcd(here):
        local('pybabel extract -F babel.cfg -o pygraz_website/translations/messages.pot pygraz_website')
        local('pybabel update -i pygraz_website/translations/messages.pot -d pygraz_website/translations')

def build():
    with lcd(here):
        local('pybabel compile -d pygraz_website/translations')
    with lcd(join(here, 'pygraz_website/static/s')):
        local('compass compile -s compressed')

from fabric.api import run
from fabric.context_managers import cd

def update():
    run('git pull origin master && git checkout -f')
    with cd('pygraz_website/static/s'):
        run('compass compile -s compact')

def reload():
    run('cat /var/run/site-www.pygraz.org.pid | xargs kill -HUP')

from docutils.core import publish_parts
from flask import current_app

def _local_tz(dt):
    return dt.astimezone(current_app.config['local_timezone'])


def timefilter(dt):
    return _local_tz(dt).time()

def datefilter(dt):
    return _local_tz(dt).strftime('%d. %b %Y')

def datetimefilter(dt):
    return _local_tz(dt)

def datecode(dt):
    return dt.strftime('%Y-%m-%d')

def datetimecode(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def rst(value):
    return publish_parts(value, writer_name='html',
            settings_overrides={'initial_header_level':2})['body']

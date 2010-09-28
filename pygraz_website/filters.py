from docutils.core import publish_parts
from flask import current_app
import pytz, datetime, urllib


def _local_tz(dt):
    return dt.astimezone(current_app.config['local_timezone'])

def timefilter(dt):
    return _local_tz(mkdate(dt)).time()

def datefilter(dt):
    return _local_tz(mkdate(dt)).strftime('%d. %b %Y')

def datetimefilter(dt):
    return _local_tz(mkdate(dt))

def datecode(dt):
    return dt.strftime('%Y-%m-%d')

def datetimecode(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def rst(value):
    return publish_parts(value, writer_name='html',
            settings_overrides={'initial_header_level':2})['body']

def mkdate(v):
    if isinstance(v, datetime.datetime):
        return v
    return datetime.datetime.utcfromtimestamp(float(v)).replace(tzinfo=pytz.utc)

def urlencode(v):
    if isinstance(v, basestring):
        return urllib.urlencode((('v', v),)).lstrip('v=')
    return urllib.urlencode(v)

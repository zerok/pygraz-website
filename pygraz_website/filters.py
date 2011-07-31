from docutils.core import publish_parts
from flask import current_app
import pytz, datetime, urllib


def _local_tz(dt):
    if dt.tzinfo is None:
        utc_dt = dt.replace(tzinfo=pytz.utc)
    else:
        utc_dt = dt
    return utc_dt.astimezone(current_app.config['local_timezone'])

def timefilter(dt):
    return _local_tz(mkdate(dt)).time()

def datefilter(dt):
    return _local_tz(mkdate(dt)).strftime('%d. %b %Y').decode('utf-8')

def datetimefilter(dt):
    return _local_tz(mkdate(dt))

def datecode(dt):
    return dt.strftime('%Y-%m-%d').decode('utf-8')

def datetimecode(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ').decode('utf-8')

def rst(value):
    return publish_parts(value, writer_name='html',
            settings_overrides={'initial_header_level':2})['body']

def mkdate(v):
    if isinstance(v, datetime.datetime):
        return v
    return datetime.datetime.utcfromtimestamp(float(v)).replace(tzinfo=pytz.utc)

def urlencode(v):
    if isinstance(v, basestring):
        return urllib.urlencode((('v', unicode(v).encode('iso8859-15')),)).lstrip('v=')
    return urllib.urlencode(v)

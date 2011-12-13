import collections
from docutils.core import publish_parts
from flask import current_app
import pytz
import datetime
import urllib
import re


WORD_SPLIT_RE = re.compile(r'\s+')

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
            settings_overrides={'initial_header_level': 2})['body']


def mkdate(v):
    if isinstance(v, datetime.datetime):
        return v
    return datetime.datetime.utcfromtimestamp(
            float(v)).replace(tzinfo=pytz.utc)


def urlencode(v):
    if isinstance(v, basestring):
        return urllib.urlencode((('v', unicode(v).encode('iso8859-15')),))\
                .lstrip('v=')
    return urllib.urlencode(v)


UrlizeResult = collections.namedtuple('UrlizeResult', 'string matches')


def urlize(v, return_matches=False):
    """
    This converts first of all link-like strings into clickable URLs but also
    detects strings like @someone and #hashtag.

    if return_matches is set to True, a dict will be returned containing a set
    of names, urls and hashtags found.
    """
    words = []
    matches = collections.defaultdict(set)
    if v is not None:
        for w in WORD_SPLIT_RE.split(v):
            prefix = ""
            suffix = ""
            if w.startswith('"') or w.startswith("'"):
                prefix = w[0]
                w = w[1:]
            if w.endswith(".") or w.endswith("'") or w.endswith('"'):
                suffix = w[-1]
                w = w[:-1]
            if w.startswith('@'):
                matches['handles'].add(w[1:])
                w = '<a href="http://twitter.com/{}">{}</a>'.format(w[1:], w)
            if w.startswith('http://') or w.startswith('https://'):
                matches['urls'].add(w)
                w = '<a href="{0}">{0}</a>'.format(w)
            if w.startswith('#'):
                matches['hashtags'].add(w[1:])
                w = '<a href="http://twitter.com/search?q=%23{}">{}</a>'.format(w[1:], w)
            words.append(u''.join([prefix, w, suffix]))
    result = u' '.join(words)
    if return_matches:
        return UrlizeResult(result, matches)
    return result
    

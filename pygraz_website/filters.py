from docutils.core import publish_parts


def timefilter(dt):
    return dt.time()

def datefilter(dt):
    return dt.strftime('%d. %b %Y')

def datecode(dt):
    return dt.strftime('%Y-%m-%d')

def datetimecode(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def rst(value):
    return publish_parts(value, writer_name='html',
            settings_overrides={'initial_header_level':2})['body']

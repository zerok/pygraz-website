from flatland.out.markup import Generator
from flask import g


def add_form_generator():
    return {'formgen': Generator(auto_for=True)}

def auth_processor():
    result = {
            'is_logged_in': False,
            'is_admin': False
            }
    if hasattr(g, 'user') and g.user is not None:
        result['is_logged_in'] = True
        if 'admin' in g.user.roles:
            result['is_admin'] = True
    return result

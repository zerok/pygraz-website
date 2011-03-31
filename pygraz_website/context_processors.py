from flatland.out.markup import Generator
from flask import g


def add_form_generator():
    """
    Injects a form generator into every page to make form processing easier.
    """
    return {'formgen': Generator(auto_for=True)}

def auth_processor():
    """
    Inject some simple account status flags into each page.
    """
    result = {
            'is_logged_in': False,
            'is_admin': False
            }
    if hasattr(g, 'user') and g.user is not None:
        result['is_logged_in'] = True
        for role in g.user.roles.all():
            if role.name == 'admin':
                result['is_admin'] = True
                break
    return result

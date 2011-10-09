from flatland.out.markup import Generator


def add_form_generator():
    """
    Injects a form generator into every page to make form processing easier.
    """
    return {'formgen': Generator(auto_for=True)}

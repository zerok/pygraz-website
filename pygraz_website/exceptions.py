from werkzeug import exceptions as wz_exceptions


class Conflict(wz_exceptions.HTTPException):
    code = 409
    description = "<p>The requested resource is currently locked</p>"

class NoEmailTemplateFound(Exception):
    def __init__(self, message, tmpls=None):
        super(Exception, self).__init__(message)
        self.tmpls = tmpls

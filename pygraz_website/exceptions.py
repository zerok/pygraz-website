from werkzeug import exceptions as wz_exceptions


class Conflict(wz_exceptions.HTTPException):
    code = 409
    description = "<p>The requested resource is currently locked</p>"

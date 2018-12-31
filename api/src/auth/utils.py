from functools import wraps

from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException


def jwt_not_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        found_jwt = False
        try:
            verify_jwt_in_request()
            found_jwt = True
        except JWTExtendedException:
            pass

        if found_jwt:
            raise JWTExtendedException("No JWT required for this endpoint")
        else:
            return fn(*args, **kwargs)

    return wrapper

from functools import wraps

from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request
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


def authorize(roles):
    def authorize_wrapper(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()
            for role in roles:
                if role in claims['roles']:
                    return fn(*args, **kwargs)
            return "You do not have access to this page, please contact your system administrator if this is a mistake.", 403

        return wrapper

    return authorize_wrapper

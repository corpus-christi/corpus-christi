from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request


def authorize(roles):
    def authorize_wrapper(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()
            for role in roles:
                if role in claims['roles']:
                    return fn(*args, **kwargs)
            return jsonify(msg='You do not have access to this page, please contact your system administrator if this is a mistake.'), 403
        return wrapper
    return authorize_wrapper

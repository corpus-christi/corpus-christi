import os
from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..people.models import Account
from .. import db
from . import etc


@etc.route('/ping')
def ping():
    """Basic smoke test that application server is running."""
    return jsonify({
        'ping': 'pong',
        'os': os.name,
        'cwd': os.getcwd(),
        'pid': os.getpid(),
        'uid': os.getuid(),
        'now': datetime.now(),
        'utc': datetime.utcnow()
    })


@etc.route('/login', methods=['POST'])
def login():
    # Construct Marshmallow-compatible error response
    err_messages = {}

    if not request.is_json:
        err_messages['payload'] = ['No payload received']
    else:
        username = request.json.get('username', None)
        if username is None:
            err_messages['username'] = ['Missing username']

        password = request.json.get('password', None)
        if password is None:
            err_messages['password'] = ['Missing password']

    if len(err_messages):
        # No point in going further without all credentials.
        return jsonify(err_messages), 400

    account = db.session.query(Account).filter_by(username=username).first()
    if account is None:
        return jsonify({ 'username': ['No such account']}), 404

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@etc.route('/login/test')
@jwt_required
def login_test():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

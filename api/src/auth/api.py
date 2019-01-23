from datetime import datetime
import datetime

from flask import jsonify, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt, get_jwt_claims

from . import auth
from .utils import jwt_not_required
from .. import jwt, db
from ..people.models import Account, AccountSchema, Person, PersonSchema, Role, RoleSchema
from .blacklist_helpers import (
    is_token_revoked, add_token_to_database, get_user_tokens,
    revoke_token, unrevoke_token,
    prune_database)

blacklist = set()

@auth.route('/login', methods=['POST'])
# @jwt_not_required
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

    # Standard vague response when credentials are wrong.
    badCred = {'login': ['Invalid credentials']}

    # Return to the caller all the account information needed.
    account = db.session.query(Account).filter_by(username=username).first()
    if account is None or not account.verify_password(password):
        return jsonify(badCred), 404

    person = db.session.query(Person).filter_by(id=account.person_id).first()
    if person is None:
        return jsonify(badCred), 404

    print(datetime)
    access_token = create_access_token(identity=username)
    # Add token to database for revokability
    add_token_to_database(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
    return jsonify(jwt=access_token, username=account.username,
                   firstName=person.first_name, lastName=person.last_name)


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    roles = db.session.query(Role).join(Account, Role.accounts).filter_by(
        username=identity).filter_by(active=True).all()
    role_schema = RoleSchema()
    user_roles = []
    for role in roles:
        user_roles.append(role_schema.dump(role)['nameI18n'])

    return {'roles': user_roles}


@auth.route('/test/jwt')
@jwt_not_required
def get_test_jwt():
    if current_app.config['TESTING']:
        access_token = create_access_token(identity='test-user')
        print("ACCESS TOKEN", access_token)
        return jsonify(jwt=access_token)
    else:
        return 'Invalid in production mode', 404


@auth.route('/test/login')
@jwt_required
def login_test():
    print("REQ", request.__dict__)
    token = get_raw_jwt()
    response = {
        'token': token,
        'timestamps': {
            'exp': datetime.fromtimestamp(token['exp']),
            'nbf': datetime.fromtimestamp(token['nbf']),
            'iat': datetime.fromtimestamp(token['iat'])
        }
    }
    username = response['username'] = get_jwt_identity()

    success = True
    account = db.session.query(Account).filter_by(username=username).first()
    if account is None:
        success = False
        response['account'] = f"Can't fetch <Account(username='{username}')>"
    else:
        account_schema = AccountSchema()
        response['account'] = account_schema.dump(account)

        person = db.session.query(Person).filter_by(
            id=account.person_id).first()
        if person is None:
            success = False
            response['person'] = f"Can't fetch <Person(id={account.person_id})>"
        else:
            person_schema = PersonSchema()
            response['person'] = person_schema.dump(person)

    response['status'] = 'success' if success else 'failure'

    return jsonify(response)


# Provide a way for a user to look at their tokens
@auth.route('/auth/token', methods=['GET'])
@jwt_required
def get_tokens():
    user_identity = get_jwt_identity()
    all_tokens = get_user_tokens(user_identity)
    ret = [token.to_dict() for token in all_tokens]
    return jsonify(ret), 200


# Provide a way for a user to revoke/unrevoke their tokens
@auth.route('/auth/token/<token_id>', methods=['PUT'])
@jwt_required
def modify_token(token_id):
    # Get and verify the desired revoked status from the body
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify(msg="Missing 'revoke' in body"), 400
    revoke = json_data.get('revoke', None)
    if revoke is None:
        return jsonify(msg="Missing 'revoke' in body"), 400
    if not isinstance(revoke, bool):
        return jsonify(msg="'revoke' must be a boolean"), 400

    # Revoke or unrevoke the token based on what was passed to this function
    user_identity = get_jwt_identity()
    try:
        if revoke:
            revoke_token(token_id, user_identity)
            return jsonify(msg='Token revoked'), 200
        else:
            unrevoke_token(token_id, user_identity)
            return jsonify(msg='Token unrevoked'), 200
    except TokenNotFound:
        return jsonify(msg='The specified token was not found'), 404
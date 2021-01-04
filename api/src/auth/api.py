import datetime
from datetime import datetime

from flask import jsonify, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from src.shared.helpers import jwt_not_required

from . import auth
from .blacklist_helpers import (
    is_token_revoked,
    add_token_to_database,
    get_user_tokens,
    revoke_token,
    unrevoke_token)
from .. import jwt, db
from ..auth.exceptions import TokenNotFound
from ..people.models import Person, PersonSchema, Role, RoleSchema
from ..people.test_people import role_object_factory, person_object_factory

blacklist = set()
person_schema = PersonSchema()


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
    person = db.session.query(Person).filter_by(username=username).first()
    if person is None or not person.verify_password(password):
        return jsonify(badCred), 404

    access_token = create_access_token(identity=person)

    # Add token to database for revokability
    add_token_to_database(
        access_token,
        current_app.config['JWT_IDENTITY_CLAIM'])

    return jsonify(jwt=access_token,
                   username=person.username,
                   firstName=person.first_name,
                   lastName=person.last_name,
                   email=person.email,
                   id=person.id)


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


@jwt.user_claims_loader
def add_claims_to_access_token(person):
    roles = person.roles
    role_schema = RoleSchema()
    user_roles = []
    for role in roles:
        user_roles.append(role_schema.dump(role)['nameI18n'])

    return {'roles': user_roles}


@jwt.user_identity_loader
def load_user_identity(person):
    return {'username': person.username, 'id': person.id}


@auth.route('/test/jwt')
@jwt_not_required
def get_test_jwt():
    if current_app.config['TESTING']:
        # TODO: parameterize the endpoint to return token with specified roles
        test_roles = [Role(**RoleSchema().load(role_object_factory()))]
        test_person = Person(**person_schema.load(person_object_factory()))
        test_person.username = 'test-user'
        test_person.roles += test_roles
        access_token = create_access_token(identity=test_person)
        add_token_to_database(access_token,
                              current_app.config['JWT_IDENTITY_CLAIM'])
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
    username = response['username'] = get_jwt_identity()['username']

    success = True
    person = db.session.query(Person).filter_by(username=username).first()
    if person is None:
        success = False
        response['person'] = f"Can't fetch <Person(username='{username}')>"
    else:
        person_schema = PersonSchema()
        response['person'] = person_schema.dump(person)

    response['status'] = 'success' if success else 'failure'

    return jsonify(response)


# Provide a way for a user to look at their tokens
@auth.route('/auth/token', methods=['GET'])
@jwt_required
def get_tokens():
    user_identity = get_jwt_identity()['username']
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
    user_identity = get_jwt_identity()['username']
    try:
        if revoke:
            revoke_token(token_id, user_identity)
            return jsonify(msg='Token revoked'), 200
        else:
            unrevoke_token(token_id, user_identity)
            return jsonify(msg='Token unrevoked'), 200
    except TokenNotFound:
        return jsonify(msg='The specified token was not found'), 404

from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt

from . import auth
from .. import db
from ..people.models import Account, AccountSchema, Person, PersonSchema


@auth.route('/login', methods=['POST'])
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

    access_token = create_access_token(identity=username)
    return jsonify(jwt=access_token, username=account.username,
                   firstName=person.first_name, lastName=person.last_name)


@auth.route('/login/test')
@jwt_required
def login_test():
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

    response['status'] = 'success'
    account = db.session.query(Account).filter_by(username=username).first()
    if account is not None:
        account_schema = AccountSchema()
        response['account'] = account_schema.dump(account)

        person = db.session.query(Person).filter_by(id=account.person_id).first()
        if person is not None:
            person_schema = PersonSchema()
            response['person'] = person_schema.dump(person)
        else:
            response['person'] = f"Can't fetch <Person(id={account.person_id})>"
    else:
        response['status'] = 'failure'

    return jsonify(response)

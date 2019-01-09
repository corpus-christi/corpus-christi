import json

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from marshmallow import ValidationError

from . import people
from .models import Person, Account, AccountSchema, PersonSchema
from .. import db

# ---- Person

person_schema = PersonSchema()


@people.route('/persons/fields', methods=['GET'])
@jwt_required
def read_person_fields():
    response = {'person': [], 'person_attributes': []}

    person_columns = Person.__table__.columns
    for c in person_columns:
        response['person'].append({c.name: c.type, 'required': not c.nullable})

    return jsonify(response)


@people.route('/persons', methods=['POST'])
@jwt_required
def create_person():
    try:
        valid_person = person_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_person = Person(**valid_person)
    db.session.add(new_person)
    db.session.commit()
    return jsonify(person_schema.dump(new_person)), 201


@people.route('/persons')
@jwt_required
def read_all_persons():
    result = db.session.query(Person).all()
    return jsonify(person_schema.dump(result, many=True))


@people.route('/persons/<person_id>')
@jwt_required
def read_one_person(person_id):
    result = db.session.query(Person).filter_by(id=person_id).first()
    return jsonify(person_schema.dump(result))


@people.route('/persons/<person_id>', methods=['PUT'])
@jwt_required
def update_person(person_id):
    try:
        valid_person = person_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    person = db.session.query(Person).filter_by(id=person_id).first()

    for key, val in valid_person.items():
        setattr(person, key, val)

    db.session.commit()

    return jsonify(person_schema.dump(person))


@people.route('/persons/deactivate/<person_id>', methods=['PUT'])
@jwt_required
def deactivate_person(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()
    account = db.session.query(Account).filter_by(id=person.account_id).first()

    if account:
        setattr(account, 'active', False)
    setattr(person, 'active', False)

    db.session.commit()

    return jsonify(person_schema.dump(person))


@people.route('/persons/activate/<person_id>', methods=['PUT'])
@jwt_required
def activate_person(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()

    setattr(person, 'active', True)

    db.session.commit()

    return jsonify(person_schema.dump(person))


# ---- Account

account_schema = AccountSchema()


@people.route('/accounts', methods=['POST'])
@jwt_required
def create_account():
    try:
        valid_account = account_schema.load(request.json)
    except ValidationError as err:
        print("ERR", err)
        return jsonify(err.messages), 422

    new_account = Account(**valid_account)
    db.session.add(new_account)
    db.session.commit()
    return jsonify(account_schema.dump(new_account)), 201


@people.route('/accounts')
@jwt_required
def read_all_accounts():
    result = db.session.query(Account).all()
    return jsonify(account_schema.dump(result, many=True))


@people.route('/accounts/<account_id>')
@jwt_required
def read_one_account(account_id):
    """Read one account by ID."""
    result = db.session.query(Account).filter_by(id=account_id).first()
    return jsonify(account_schema.dump(result))


@people.route('/accounts/username/<username>')
@jwt_required
def read_one_account_by_username(username):
    """Read one account by its (unique) user name."""
    result = db.session.query(Account).filter_by(username=username).first()
    return jsonify(account_schema.dump(result))


@people.route('/persons/<person_id>/account')
@jwt_required
def read_person_account(person_id):
    account = db.session.query(Account).filter_by(person_id=person_id).first()
    return jsonify(account_schema.dump(account))


@people.route('/accounts/<account_id>', methods=['PATCH'])
@jwt_required
def update_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'not found', 404

    # Only these fields can be meaningfully updated.
    for field in 'password', 'username', 'active':
        if field in request.json:
            setattr(account, field, request.json[field])
    db.session.commit()
    return jsonify(account_schema.dump(account))


@people.route('/accounts/deactivate/<account_id>', methods=['PUT'])
@jwt_required
def deactivate_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()

    setattr(account, 'active', False)

    db.session.commit()

    return jsonify(account_schema.dump(account))


@people.route('/accounts/activate/<account_id>', methods=['PUT'])
@jwt_required
def activate_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()

    setattr(account, 'active', True)

    db.session.commit()

    return jsonify(account_schema.dump(account))
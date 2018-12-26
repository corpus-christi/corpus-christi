from flask import request
from flask.json import jsonify
from marshmallow import ValidationError

from . import people
from .models import Person, Account, AccountSchema, PersonSchema
from .. import db

# ---- Person

person_schema = PersonSchema()


@people.route('/persons', methods=['POST'])
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
def read_all_persons():
    result = db.session.query(Person).all()
    return jsonify(person_schema.dump(result, many=True))


@people.route('/persons/<person_id>')
def read_one_person(person_id):
    result = db.session.query(Person).filter_by(id=person_id).first()
    return jsonify(person_schema.dump(result))


@people.route('/persons/<person_id>', methods=['PUT'])
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


# ---- Account

account_schema = AccountSchema()


@people.route('/accounts', methods=['POST'])
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
def read_all_accounts():
    result = db.session.query(Account).all()
    return jsonify(account_schema.dump(result, many=True))


@people.route('/accounts/<account_id>')
def read_one_account(account_id):
    result = db.session.query(Account).filter_by(id=account_id).first()
    return jsonify(account_schema.dump(result))


@people.route('/persons/<person_id>/account')
def read_person_account(person_id):
    account = db.session.query(Account).filter_by(person_id=person_id).first()
    return jsonify(account_schema.dump(account))


@people.route('/accounts/<account_id>', methods=['PATCH'])
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

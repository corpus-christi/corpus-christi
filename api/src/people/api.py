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


# ---- Account

account_schema = AccountSchema()


@people.route('/accounts', methods=['POST'])
def create_account():
    try:
        valid_account = account_schema.load(request.json)
    except ValidationError as err:
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

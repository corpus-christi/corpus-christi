from flask import request
from flask.json import jsonify
from marshmallow import ValidationError

from . import people
from .models import Person, PersonSchema
from .. import db

person_schema = PersonSchema()


# ---- Person

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

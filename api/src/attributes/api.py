import json

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from marshmallow import ValidationError

from . import attributes
from ..people.models import Person, Account
from .models import Attribute, AttributeSchema, Enumerated_Value, Enumerated_ValueSchema, Person_Attribute, Person_AttributeSchema
from .. import db


# ---- Attribute

attribute_schema = AttributeSchema()


@attributes.route('/attributes', methods=['POST'])
@jwt_required
def create_attribute():
    try:
        valid_attribute = attribute_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_attribute = Attribute(**valid_attribute)
    db.session.add(new_attribute)
    db.session.commit()
    return jsonify(attribute_schema.dump(new_attribute)), 201


@attributes.route('/attributes')
@jwt_required
def read_all_attributes():
    result = db.session.query(Attribute).all()
    return jsonify(attribute_schema.dump(result, many=True))


@attributes.route('/attributes/<attribute_id>')
@jwt_required
def read_one_attribute(attribute_id):
    result = db.session.query(Attribute).filter_by(id=attribute_id).first()
    return jsonify(attribute_schema.dump(result))


@attributes.route('/attributes/<attribute_id>', methods=['PUT'])
@jwt_required
def replace_attribute(attribute_id):
    pass


@attributes.route('/attributes/<attribute_id>', methods=['PATCH'])
@jwt_required
def update_attribute(attribute_id):
    try:
        valid_attribute = attribute_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    attribute = db.session.query(Attribute).filter_by(id=attribute_id).first()

    for key, val in valid_attribute.items():
        setattr(attribute, key, val)

    db.session.commit()
    return jsonify(attribute_schema.dump(attribute))


@attributes.route('/attributes/disable/<attribute_id>', methods=['PATCH'])
@jwt_required
def disable_attribute(attribute_id):
    attribute = db.session.query(Attribute).filter_by(id=attribute_id).first()

    setattr(attribute, 'active', False)

    db.session.commit()

    return jsonify(attribute_schema.dump(attribute))


# ---- Enumerated_Value

enumerated_value_schema = Enumerated_ValueSchema()


@attributes.route('/enumerated_values', methods=['POST'])
@jwt_required
def create_enumerated_value():
    try:
        valid_enumerated_value = enumerated_value_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_enumerated_value = Enumerated_Value(**valid_enumerated_value)
    db.session.add(new_enumerated_value)
    db.session.commit()
    return jsonify(enumerated_value_schema.dump(new_enumerated_value)), 201


@attributes.route('/enumerated_values')
@jwt_required
def read_all_enumerated_values():
    result = db.session.query(Enumerated_Value).all()
    return jsonify(enumerated_value_schema.dump(result, many=True))


@attributes.route('/enumerated_values/<enumerated_value_id>')
@jwt_required
def read_one_enumerated_value(enumerated_value_id):
    result = db.session.query(Enumerated_Value).filter_by(
        id=enumerated_value_id).first()
    return jsonify(enumerated_value_schema.dump(result))


@attributes.route('/enumerated_values/<enumerated_value_id>', methods=['PATCH'])
@jwt_required
def update_enumerated_value(enumerated_value_id):
    try:
        valid_enumerated_value = enumerated_value_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    enumerated_value = db.session.query(
        Enumerated_Value).filter_by(id=enumerated_value_id).first()

    for key, val in valid_enumerated_value.items():
        setattr(enumerated_value, key, val)

    db.session.commit()
    return jsonify(enumerated_value_schema.dump(enumerated_value))


@attributes.route('/enumerated_values/disable/<enumerated_value_id>', methods=['PATCH'])
@jwt_required
def disable_enumerated_value(enumerated_value_id):
    enumerated_value = db.session.query(
        Enumerated_Value).filter_by(id=enumerated_value_id).first()

    setattr(enumerated_value, 'active', False)

    db.session.commit()

    return jsonify(attribute_schema.dump(attribute))


# ---- Person_Attribute

person_attribute_schema = Person_AttributeSchema()


@attributes.route('/person_attributes', methods=['POST'])
@jwt_required
def create_person_attribute():
    try:
        valid_person_attribute = person_attribute_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_person_attribute = Person_Attribute(**valid_person_attribute)
    db.session.add(new_person_attribute)
    db.session.commit()
    return jsonify(person_attribute_schema.dump(new_person_attribute)), 201


@attributes.route('/person_attributes')
@jwt_required
def read_all_person_attributes():
    result = db.session.query(Person_Attribute).all()
    return jsonify(person_attribute_schema.dump(result, many=True))


@attributes.route('/person_attributes/<person_attribute_id>')
@jwt_required
def read_one_person_attribute(person_attribute_id):
    result = db.session.query(Person_Attribute).filter_by(
        id=person_attribute_id).first()
    return jsonify(person_attribute_schema.dump(result))


@attributes.route('/person_attributes/<person_attribute_id>', methods=['PUT'])
@jwt_required
def replace_person_attribute(person_attribute_id):
    pass


@attributes.route('/person_attributes/<person_attribute_id>', methods=['PATCH'])
@jwt_required
def update_person_attribute(person_attribute_id):
    try:
        valid_person_attribute = person_attribute_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    person_attribute = db.session.query(
        Person_Attribute).filter_by(id=person_attribute_id).first()

    for key, val in valid_person_attribute.items():
        setattr(person_attribute, key, val)

    db.session.commit()
    return jsonify(person_attribute_schema.dump(person_attribute))


@attributes.route('/person_attributes/<person_attribute_id>', methods=['DELETE'])
@jwt_required
def delete_person_attribute(person_attribute_id):
    pass

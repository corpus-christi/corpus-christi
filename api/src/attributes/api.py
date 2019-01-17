import json

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from marshmallow import ValidationError

from . import attributes
from ..people.models import Person, Account
from .models import Attribute, AttributeSchema, EnumeratedValue, EnumeratedValueSchema, PersonAttribute, PersonAttributeSchema
from .. import db


# ---- Attribute

attribute_schema = AttributeSchema()
enumerated_value_schema = EnumeratedValueSchema(exclude=['id'])
enumerated_value_schema_with_id = EnumeratedValueSchema()


@attributes.route('/attributes', methods=['POST'])
@jwt_required
def create_attribute():
    try:
        valid_attribute = attribute_schema.load(request.json['attribute'])
        valid_enumerated_values = enumerated_value_schema.load(
            request.json['enumeratedValues'], many=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_attribute = Attribute(**valid_attribute)
    db.session.add(new_attribute)
    db.session.commit()

    for enumerated_value in valid_enumerated_values:
        enumerated_value = EnumeratedValue(**enumerated_value)
        enumerated_value.attribute_id = new_attribute.id
        db.session.add(enumerated_value)

    db.session.commit()
    result = db.session.query(Attribute).filter_by(id=new_attribute.id).first()
    result.enumerated_values = result.enumerated_values
    return jsonify(attribute_schema.dump(result)), 201


@attributes.route('/attributes')
@jwt_required
def read_all_attributes():
    result = db.session.query(Attribute).filter_by(active=True).all()
    return jsonify(attribute_schema.dump(result, many=True))


@attributes.route('/attributes/<attribute_id>')
@jwt_required
def read_one_attribute(attribute_id):
    result = db.session.query(Attribute).filter_by(id=attribute_id).first()
    return jsonify(attribute_schema.dump(result))


@attributes.route('/attributes/<attribute_id>', methods=['PATCH'])
@jwt_required
def update_attribute(attribute_id):
    update_enumerated_values = []
    new_enumerated_values = []

    try:
        valid_attribute = attribute_schema.load(request.json['attribute'])
        for enumerated_value in request.json['enumeratedValues']:
            if 'id' in enumerated_value.keys():
                update_enumerated_values.append(
                    enumerated_value_schema_with_id.load(enumerated_value))
            else:
                new_enumerated_values.append(
                    enumerated_value_schema.load(enumerated_value))
    except ValidationError as err:
        return jsonify(err.messages), 422

    for new_enumerated_value in new_enumerated_values:
        new_enumerated_value = EnumeratedValue(**new_enumerated_value)
        new_enumerated_value.attribute_id = attribute_id
        db.session.add(new_enumerated_value)

    for update_enumerated_value in update_enumerated_values:
        old_enumerated_value = db.session.query(EnumeratedValue).filter_by(
            attribute_id=attribute_id, id=update_enumerated_value['id']).first()
        if old_enumerated_value is not None:
            setattr(old_enumerated_value, 'value_i18n',
                    update_enumerated_value['value_i18n'])

    attribute = db.session.query(Attribute).filter_by(id=attribute_id).first()

    for key, val in valid_attribute.items():
        setattr(attribute, key, val)

    db.session.commit()
    result = db.session.query(Attribute).filter_by(id=attribute.id).first()
    result.enumerated_values = result.enumerated_values
    return jsonify(attribute_schema.dump(attribute))


@attributes.route('/attributes/deactivate/<attribute_id>', methods=['PATCH'])
@jwt_required
def deactivate_attribute(attribute_id):
    attribute = db.session.query(Attribute).filter_by(id=attribute_id).first()

    setattr(attribute, 'active', False)

    db.session.commit()

    return jsonify(attribute_schema.dump(attribute))


@attributes.route('/attributes/activate/<attribute_id>', methods=['PATCH'])
@jwt_required
def activate_attribute(attribute_id):
    attribute = db.session.query(Attribute).filter_by(id=attribute_id).first()

    setattr(attribute, 'active', True)

    db.session.commit()

    return jsonify(attribute_schema.dump(attribute))


# ---- EnumeratedValue


@attributes.route('/enumerated_values', methods=['POST'])
@jwt_required
def create_enumerated_value():
    try:
        valid_enumerated_value = enumerated_value_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_enumerated_value = EnumeratedValue(**valid_enumerated_value)
    db.session.add(new_enumerated_value)
    db.session.commit()
    return jsonify(enumerated_value_schema.dump(new_enumerated_value)), 201


@attributes.route('/enumerated_values')
@jwt_required
def read_all_enumerated_values():
    result = db.session.query(EnumeratedValue).all()
    return jsonify(enumerated_value_schema.dump(result, many=True))


@attributes.route('/enumerated_values/<enumerated_value_id>')
@jwt_required
def read_one_enumerated_value(enumerated_value_id):
    result = db.session.query(EnumeratedValue).filter_by(
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
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    for key, val in valid_enumerated_value.items():
        setattr(enumerated_value, key, val)

    db.session.commit()
    return jsonify(enumerated_value_schema.dump(enumerated_value))


@attributes.route('/enumerated_values/deactivate/<enumerated_value_id>', methods=['PATCH'])
@jwt_required
def deactivate_enumerated_value(enumerated_value_id):
    enumerated_value = db.session.query(
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    setattr(enumerated_value, 'active', False)

    db.session.commit()

    return jsonify(enumerated_value_schema.dump(enumerated_value))


@attributes.route('/enumerated_values/activate/<enumerated_value_id>', methods=['PATCH'])
@jwt_required
def activate_enumerated_value(enumerated_value_id):
    enumerated_value = db.session.query(
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    setattr(enumerated_value, 'active', True)

    db.session.commit()

    return jsonify(enumerated_value_schema.dump(enumerated_value))




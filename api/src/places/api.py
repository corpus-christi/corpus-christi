from flask import request, jsonify
from marshmallow import Schema, fields
from marshmallow.validate import Length
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional

from .. import db
from ..i18n.models import I18NValue, I18NKey
from . import places
from .models import Country, Address, AddressSchema, Area, AreaSchema, Location, LocationSchema


def modify_entity(entity_type, schema, id, new_value_dict):
    item = db.session.query(entity_type).filter_by(id=id).first()

    if not item:
        return jsonify(f"Item with id #{id} does not exist."), 404

    for key, val in new_value_dict.items():
        setattr(item, key, val)
    
    db.session.commit()

    return jsonify(schema.dump(item)), 200



class CountryListSchema(Schema):
    code = fields.String(required=True, validate=Length(equal=2))
    name = fields.String(attribute="gloss", required=True, validate=Length(min=1))


country_list_schema = CountryListSchema()


@places.route('/countries')
@places.route('/countries/<country_code>')
def read_countries(country_code=None):
    locale_code = request.args.get('locale')
    if locale_code is None:
        return 'Missing locale', 400

    if country_code is None:
        result = db.session \
            .query(Country.code, I18NValue.gloss) \
            .join(I18NKey, I18NValue) \
            .filter_by(locale_code=locale_code) \
            .all()
        return jsonify(country_list_schema.dump(result, many=True))
    else:
        result = db.session \
            .query(Country.code, I18NValue.gloss) \
            .filter_by(code=country_code) \
            .join(I18NKey, I18NValue) \
            .filter_by(locale_code=locale_code) \
            .first()
    return jsonify(country_list_schema.dump(result))


# ---- Area

area_schema = AreaSchema()


@places.route('/areas', methods=['POST'])
@jwt_required
def create_area():
    try:
        valid_area = area_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_area = Area(**valid_area)
    db.session.add(new_area)
    db.session.commit()
    return jsonify(area_schema.dump(new_area)), 201


@places.route('/areas')
@jwt_required
def read_all_areas():
    result = db.session.query(Area).all()
    return jsonify(area_schema.dump(result, many=True))


@places.route('/areas/<area_id>')
@jwt_required
def read_one_area(area_id):
    result = db.session.query(Area).filter_by(id=area_id).first()
    return jsonify(area_schema.dump(result))


@places.route('/areas/<area_id>', methods=['PUT'])
@jwt_required
def replace_area(area_id):
    pass


@places.route('/areas/<area_id>', methods=['PATCH'])
@jwt_required
def update_area(area_id):
    try:
        valid_area = area_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    area = db.session.query(Area).filter_by(id=area_id).first()

    for key, val in valid_area.items():
        setattr(area, key, val)

    db.session.commit()
    return jsonify(area_schema.dump(area))


@places.route('/areas/<area_id>', methods=['DELETE'])
@jwt_required
def delete_area(area_id):
    pass


# ---- Address

address_schema = AddressSchema()


@places.route('/addresses', methods=['POST'])
@jwt_required
def create_address():
    try:
        valid_address = address_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_address = Address(**valid_address)
    db.session.add(new_address)
    db.session.commit()
    return jsonify(address_schema.dump(new_address)), 201


@places.route('/addresses')
@jwt_required
def read_all_addresses():
    result = db.session.query(Address).all()
    return jsonify(address_schema.dump(result, many=True))


@places.route('/addresses/<address_id>')
@jwt_required
def read_one_address(address_id):
    result = db.session.query(Address).filter_by(id=address_id).first()
    return jsonify(address_schema.dump(result))


@places.route('/addresses/<address_id>', methods=['PUT'])
@jwt_required
def replace_address(address_id):
    try: 
        valid_attributes = address_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_address(address_id, valid_attributes)


@places.route('/addresses/<address_id>', methods=['PATCH'])
@jwt_required
def update_address(address_id):
    try: 
        valid_attributes = address_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_address(address_id, valid_attributes)


@places.route('/addresses/<address_id>', methods=['DELETE'])
@jwt_required
def delete_address(address_id):
    address_asset = db.session.query(Address).filter_by(id=address_id).first()

    if not address_asset:
        return jsonify(f"Address with id #{address_id} does not exist."), 404

    db.session.delete(address_asset)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully deleted', 204


def modify_address(address_id, address_object):
    return modify_entity(Address, address_schema, address_id, address_object)


# ---- Location

location_schema = LocationSchema()


@places.route('/locations', methods=['POST'])
@jwt_required
def create_location():
    try:
        valid_location = location_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_location = Location(**valid_location)
    db.session.add(new_location)
    db.session.commit()
    return jsonify(location_schema.dump(new_location)), 201


@places.route('/locations')
@jwt_required
def read_all_locations():
    result = db.session.query(Location).all()
    return jsonify(location_schema.dump(result, many=True))


@places.route('/locations/<location_id>')
@jwt_required
def read_one_location(location_id):
    result = db.session.query(Location).filter_by(id=location_id).first()
    return jsonify(location_schema.dump(result))


@places.route('/locations/<location_id>', methods=['PUT'])
@jwt_required
def replace_location(location_id):
    try:
        valid_location = location_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_location(location_id, valid_location)


@places.route('/locations/<location_id>', methods=['PATCH'])
@jwt_required
def update_location(location_id):
    try: 
        valid_attributes = location_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_location(location_id, valid_attributes)


@places.route('/locations/<location_id>', methods=['DELETE'])
@jwt_required
def delete_location(location_id):
    location_asset = db.session.query(Location).filter_by(id=location_id).first()

    if not location_asset:
        return jsonify(f"Location with id #{location_id} does not exist."), 404

    db.session.delete(location_asset)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully deleted', 204


def modify_location(location_id, location_object):
    return modify_entity(Location, location_schema, location_id, location_object)

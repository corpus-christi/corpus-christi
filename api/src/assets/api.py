from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import func

from . import assets
from .models import Asset, AssetSchema
from .. import db
from ..etc.helper import modify_entity, get_exclusion_list
from ..events.models import EventAsset


# ---- Asset

@assets.route('/', methods=['POST'])
@jwt_required
def create_asset():
    asset_schema = AssetSchema(exclude=get_exclusion_list(request.args, ['location']))
    try:
        valid_asset = asset_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_asset = Asset(**valid_asset)
    db.session.add(new_asset)
    db.session.commit()
    return jsonify(asset_schema.dump(new_asset)), 201


@assets.route('/')
@jwt_required
def read_all_assets():
    asset_schema = AssetSchema(exclude=get_exclusion_list(request.args, ['location']))
    query = db.session.query(Asset).add_columns(func.count(EventAsset.event_id).label('event_count'))

    # -- return_inactives --
    # Filter assets based on active status
    return_group = request.args.get('return_group')
    if return_group == 'inactive':
        query = query.filter_by(active=False)
    elif return_group in ('all', 'both'):
        pass  # Don't filter
    else:
        query = query.filter_by(active=True)

    # -- description --
    # Filter events on a wildcard description string
    desc_filter = request.args.get('desc')
    if desc_filter:
        query = query.filter(Asset.description.like(f"%{desc_filter}%"))

    # -- location --
    # Filter events on a wildcard location string?
    location_filter = request.args.get('location_id')
    if location_filter:
        query = query.filter_by(location_id=location_filter)

    # Sorting
    sort_filter = request.args.get('sort')
    if sort_filter:
        sort_column = None
        if sort_filter[:11] == 'description':
            sort_column = Asset.description

        if sort_filter[-4:] == 'desc' and sort_column:
            sort_column = sort_column.desc()

        query = query.order_by(sort_column)

    result = query.join(EventAsset, isouter=True).group_by(Asset.id).all()

    temp_result = list()
    for item in result:
        temp_result.append(asset_schema.dump(item[0]))
        temp_result[-1]['event_count'] = item[1]

    return jsonify(asset_schema.dump(temp_result, many=True))


@assets.route('/<asset_id>')
@jwt_required
def read_one_asset(asset_id):
    asset_schema = AssetSchema(exclude=get_exclusion_list(request.args, ['location']))
    asset = db.session.query(Asset).filter_by(id=asset_id).add_columns(
        func.count(EventAsset.event_id).label('event_count')).join(EventAsset, isouter=True).group_by(Asset.id).first()

    if not asset:
        return jsonify(f"Asset with id #{asset_id} does not exist."), 404

    result = asset_schema.dump(asset[0])
    result['event_count'] = asset[1]

    return jsonify(asset_schema.dump(result))


@assets.route('/<asset_id>', methods=['PUT'])
@jwt_required
def replace_asset(asset_id):
    asset_schema = AssetSchema(exclude=get_exclusion_list(request.args, ['location']))
    try:
        valid_asset = asset_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_entity(Asset, asset_schema, asset_id, valid_asset)


@assets.route('/<asset_id>', methods=['PATCH'])
@jwt_required
def update_asset(asset_id):
    asset_schema = AssetSchema(exclude=get_exclusion_list(request.args, ['location']))
    try:
        valid_attributes = asset_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_entity(Asset, asset_schema, asset_id, valid_attributes)


@assets.route('/<asset_id>', methods=['DELETE'])
@jwt_required
def delete_asset(asset_id):
    asset = db.session.query(Asset).filter_by(id=asset_id).first()

    if not asset:
        return jsonify(f"Event with id #{asset_id} does not exist."), 404

    setattr(asset, 'active', False)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully deleted asset', 204

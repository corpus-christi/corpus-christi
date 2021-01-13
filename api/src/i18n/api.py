from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_claims
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length

from . import i18n
from .models import I18NLocale, I18NLocaleSchema, I18NKeySchema, I18NKey, I18NValue, I18NMultipleLocalesPreSplit, I18NMultipleLocalesSplitKey, I18NValueSchema, Language
from .. import db
from ..shared.helpers import list_to_tree, BadListKeyPath
from ..shared.helpers import logged_response, authorize

from sqlalchemy.orm import aliased
import re

# ---- I18N Locale

i18n_locale_schema = I18NLocaleSchema()


@i18n.route('/locales')
def read_all_locales():
    locales = db.session.query(I18NLocale).all()
    return jsonify(i18n_locale_schema.dump(locales, many=True))


@i18n.route('/locales/<locale_code>')
def read_one_locale(locale_code):
    locale = db.session.query(I18NLocale).filter_by(code=locale_code).first()
    if locale is None:
        return 'No such locale', 404
    else:
        return jsonify(i18n_locale_schema.dump(locale))


@i18n.route('/locales', methods=['POST'])
@jwt_required
def create_locale():
    try:
        loaded = i18n_locale_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_locale = I18NLocale(**request.json)
    db.session.add(new_locale)
    db.session.commit()
    return jsonify(i18n_locale_schema.dump(new_locale)), 201


@i18n.route('/locales/<locale_code>', methods=['DELETE'])
@jwt_required
def delete_one_locale(locale_code):
    locale = db.session.query(I18NLocale).get(locale_code)
    db.session.delete(locale)
    db.session.commit()
    return 'ok', 204


# ---- I18N Key

i18n_key_schema = I18NKeySchema()


@i18n.route('/keys')
def read_all_keys():
    keys = db.session.query(I18NKey).all()
    return jsonify(i18n_key_schema.dump(keys, many=True))


@i18n.route('/keys/<key_id>')
def read_one_key(key_id):
    key = db.session.query(I18NKey).filter_by(id=key_id).first()
    if key is None:
        return 'No such key', 404
    else:
        return jsonify(i18n_key_schema.dump(key))


@i18n.route('/keys', methods=['POST'])
@jwt_required
def create_key():
    try:
        loaded = i18n_key_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_key = I18NKey(**request.json)
    db.session.add(new_key)
    db.session.commit()
    return jsonify(i18n_key_schema.dump(new_key)), 201


# ---- I18N Value

i18n_value_schema = I18NValueSchema()
i18n_multiple_locales_pre_split = I18NMultipleLocalesPreSplit()
i18n_multiple_locales_split_key = I18NMultipleLocalesSplitKey()

@i18n.route('/values')
def read_all_values():
    values = db.session.query(I18NValue).all()
    return jsonify(i18n_value_schema.dump(values, many=True))


@i18n.route('/values/update', methods=['PATCH'])
@authorize(['role.translator'])
@jwt_required
def update_a_value():
    #     update the values with the info in payload
    i18n_value_schema = I18NValueSchema()

    #     verify_jwt_in_request()
    claims = get_jwt_claims()
    if 'role.translator' not in claims['roles']:
        return 'Permission denied', 403
    else:
        try:
            valid_attributes = i18n_value_schema.load(request.json, partial=True)
        except ValidationError as err:
            return logged_response(err.messages, 422)

        i18n_value = db.session.query(I18NValue).filter_by(locale_code=valid_attributes.get('locale_code'),
                                                           key_id=valid_attributes.get('key_id')).first()

    i18n_value = db.session.query(I18NValue).filter_by(
        locale_code=valid_attributes.get('locale_code'),
        key_id=valid_attributes.get('key_id')).first()

    if not i18n_value:
        return logged_response(
            f"Group with key_id #{valid_attributes['key_id']} does not exist.", 404)

    for key, val in valid_attributes.items():
        setattr(i18n_value, key, val)

    db.session.add(i18n_value)
    db.session.commit()

    return logged_response(i18n_value_schema.dump(i18n_value), 200)


@i18n.route('/values/<locale_code>')
def read_xlation(locale_code):
    # Check that the locale exists.
    locale = db.session.query(I18NLocale).filter_by(code=locale_code).first()
    if locale is None:
        return 'Locale not found', 404

    # Fetch the values for this locale
    values = db.session.query(I18NValue).filter_by(locale_code=locale_code)

    # Format the response.
    format = request.args.get('format', 'list')
    if format == 'list':
        # Return the values as a simple list.
        return jsonify(i18n_value_schema.dump(values, many=True))
    elif format == 'tree':
        # Interpret keys as a hierarchical structure.
        # Tree-building idea from  https://stackoverflow.com/questions/16547643
        entries = map(
            lambda value: {
                'path': value.key_id,
                'value': value.gloss},
            values)
        try:
            tree = list_to_tree(entries)
        except BadListKeyPath as e:
            return str(e), 400
        return jsonify(tree)
    else:
        return 'Invalid format', 400


@i18n.route('/values/translations/<preview_locale_str>/<current_locale_str>')
def fetch_and_format_target_locales(preview_locale_str, current_locale_str):
    preview_locale = db.session.query(I18NLocale).filter_by(code=preview_locale_str).first()
    current_locale = db.session.query(I18NLocale).filter_by(code=current_locale_str).first()
    if preview_locale_str == current_locale_str:
        return 'Locales may not be identical', 400
    if preview_locale is None or current_locale is None:
        return 'At least one locale not found', 404

    i18n_preview = aliased(I18NValue)
    i18n_current = aliased(I18NValue)
    pre_split_values = db.session.query(i18n_preview, i18n_current).with_entities(
        i18n_preview.key_id.label('key_id'),
        i18n_preview.gloss.label('preview_gloss'),
        i18n_current.gloss.label('current_gloss'),
        i18n_current.verified.label('current_verified')
    ).filter(
        i18n_preview.locale_code == preview_locale_str,
        i18n_current.locale_code == current_locale_str,
        i18n_preview.key_id == i18n_current.key_id
    ).order_by(i18n_preview.key_id).all()

    split_values = i18n_multiple_locales_pre_split.dump(pre_split_values, many=True)    
    for item in split_values:
        matches = re.match("(.+?)\.(.+)", item['key_id']) # (first).(second.third.fourth.etc)
        item.pop('key_id', None)
        item['top_level_key'] = matches.groups()[0]
        item['rest_of_key'] = matches.groups()[1]

    return jsonify(i18n_multiple_locales_split_key.dump(split_values, many=True))


# ---- Language

class LanguageSchema(Schema):
    code = fields.String(required=True, validate=Length(equal=2))
    name = fields.String(
        attribute="gloss",
        required=True,
        validate=Length(
            min=1))


language_schema = LanguageSchema()


@i18n.route('/languages')
@i18n.route('/languages/<language_code>')
def read_languages(language_code=None):
    locale_code = request.args.get('locale')
    if locale_code is None:
        return 'Missing locale', 400

    if language_code is None:
        result = db.session \
            .query(Language.code, I18NValue.gloss) \
            .join(Language.key) \
            .join(I18NKey.values) \
            .filter_by(locale_code=locale_code) \
            .all()
        return jsonify(language_schema.dump(result, many=True))
    else:
        result = db.session \
            .query(Language.code, I18NValue.gloss) \
            .filter_by(code=language_code) \
            .join(Language.key) \
            .join(I18NKey.values) \
            .filter_by(locale_code=locale_code) \
            .first()
        return jsonify(language_schema.dump(result))

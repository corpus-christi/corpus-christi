from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length

from ..import db
from . import i18n
from .models import I18NLocale, I18NLocaleSchema, I18NKeySchema, I18NKey, I18NValue, I18NValueSchema, Language

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


@i18n.route('/values')
def read_all_values():
    values = db.session.query(I18NValue).all()
    return jsonify(i18n_value_schema.dump(values, many=True))


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
        tree = {}
        for value in values:
            t = tree
            keys = value.key_id.split('.')
            for idx, key in enumerate(keys):
                if idx < len(keys) - 1:
                    # Intermediate "node"; add another dictionary
                    t = t.setdefault(key, {})
                else:
                    # Last node
                    if isinstance(t, dict):
                        # Set key-value in leaf node of tree
                        t[key] = value.gloss
                    else:
                        # Already a string value for this key
                        return f'Invalid key ({value.key_id})', 400
        return jsonify(tree)
    else:
        return 'Invalid format', 400


# ---- Language


class LanguageSchema(Schema):
    code = fields.String(required=True, validate=Length(equal=2))
    name = fields.String(attribute="gloss", required=True, validate=Length(min=1))


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
            .join(I18NKey, I18NValue) \
            .filter_by(locale_code=locale_code) \
            .all()
        return jsonify(language_schema.dump(result, many=True))
    else:
        result = db.session \
            .query(Language.code, I18NValue.gloss) \
            .filter_by(code=language_code) \
            .join(I18NKey, I18NValue) \
            .filter_by(locale_code=locale_code) \
            .first()
        return jsonify(language_schema.dump(result))

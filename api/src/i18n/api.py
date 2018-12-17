from flask import request, jsonify
from marshmallow import ValidationError

from . import i18n
from .. import orm
from src.i18n.models import I18NLocale, I18NLocaleSchema, I18NKeySchema, I18NKey, I18NValue, I18NValueSchema

i18n_locale_schema = I18NLocaleSchema()
i18n_key_schema = I18NKeySchema()
i18n_value_schema = I18NValueSchema()


# ---- Locale

@i18n.route('/locales')
def read_all_locales():
    locales = I18NLocale.query.all()
    return i18n_locale_schema.jsonify(locales, many=True)


@i18n.route('/locales/<locale_id>')
def read_one_locale(locale_id):
    locale = I18NLocale.query.filter_by(id=locale_id).first()
    if locale is None:
        return 'No such locale', 404
    else:
        return i18n_locale_schema.jsonify(locale)


@i18n.route('/locales', methods=['POST'])
def create_locale():
    try:
        loaded = i18n_locale_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_locale = I18NLocale(**request.json)
    orm.session.add(new_locale)
    orm.session.commit()
    return i18n_locale_schema.jsonify(new_locale), 201


@i18n.route('/locales/<locale_id>', methods=['DELETE'])
def delete_one_locale(locale_id):
    locale = I18NLocale.query.get_or_404(locale_id)
    orm.session.delete(locale)
    orm.session.commit()
    return 'ok', 204


# ---- Keys

@i18n.route('/keys')
def read_all_keys():
    keys = I18NKey.query.all()
    return i18n_key_schema.jsonify(keys, many=True)


@i18n.route('/keys/<key_id>')
def read_one_key(key_id):
    key = I18NKey.query.filter_by(id=key_id).first()
    if key is None:
        return 'No such key', 404
    else:
        return i18n_key_schema.jsonify(key)


@i18n.route('/keys', methods=['POST'])
def create_key():
    try:
        loaded = i18n_key_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_key = I18NKey(**request.json)
    orm.session.add(new_key)
    orm.session.commit()
    return i18n_key_schema.jsonify(new_key), 201


# ---- Values

@i18n.route('/values')
def read_all_values():
    values = I18NValue.query.all()
    return i18n_value_schema.jsonify(values, many=True)

@i18n.route('/values/<locale_id>')
def read_xlation(locale_id):
    values = I18NKey.query.join(I18NValue).join(I18NLocale).filter(I18NLocale.id==locale_id).all()
    print(values)
    return 'ok'

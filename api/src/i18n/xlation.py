from flask import request, jsonify

from . import i18n
from .. import db
from ..models import I18NLocale, I18NLocaleSchema

i18n_locale_schema = I18NLocaleSchema()


@i18n.route('/locales')
@i18n.route('/locales/<locale_id>')
def read_locales(locale_id=None):
    if locale_id is None:
        locales = I18NLocale.query.all()
        return i18n_locale_schema.jsonify(locales, True)
    else:
        locale = I18NLocale.query.filter_by(id=locale_id).first()
        return i18n_locale_schema.jsonify(locale)


@i18n.route('/locales', methods=['POST'])
def create_locale():
    loaded = i18n_locale_schema.load(request.json)
    print(loaded)

    new_locale = I18NLocale(**request.json)     # FIXME What about validation?!
    db.session.add(new_locale)
    db.session.commit()
    return i18n_locale_schema.jsonify(new_locale)


@i18n.route('/locales/<locale_id>', methods=['DELETE'])
def delete_locale(locale_id):
    locale = I18NLocale.query.get_or_404(locale_id)
    db.session.delete(locale)
    db.session.commit()
    return 'ok'

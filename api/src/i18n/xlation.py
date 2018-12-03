from flask import request
from flask.json import jsonify

from . import i18n
from .. import db
from ..models import I18NLocale


@i18n.route('/locales/')
@i18n.route('/locales/<locale_id>')
def read_locales(locale_id=None):
    if locale_id is None:
        return jsonify([locale.to_json() for locale in I18NLocale.query.all()])
    else:
        locale = I18NLocale.query.filter_by(id=locale_id)
        return jsonify(locale[0].to_json())


@i18n.route('/locales/', methods=['POST'])
def create_locale():
    new_locale = I18NLocale(id=request.json['id'], desc=request.json['desc'])
    db.session.add(new_locale)
    db.session.commit()
    return 'ok'


@i18n.route('/locales/<locale_id>', methods=['DELETE'])
def delete_locale(locale_id):
    locale = I18NLocale.query.get_or_404(locale_id)
    db.session.delete(locale)
    db.session.commit()
    return 'ok'

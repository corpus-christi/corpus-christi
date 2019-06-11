from . import db
from .i18n.models import I18NValue, I18NValueSchema
from flask.json import jsonify


def getTranslation(locale_code, i18n_key):
    i18n_schema = I18NValueSchema()
    res = db.session.query(I18NValue).filter_by(
        key_id=i18n_key, locale_code=locale_code).first()
    print(jsonify(i18n_schema.dump(res)))
    return False

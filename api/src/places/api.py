from flask import request, jsonify
from marshmallow import Schema, fields
from marshmallow.validate import Length

from src import db
from src.i18n.models import I18NValue, I18NKey
from . import places
from .models import Country


class CountryListSchema(Schema):
    code = fields.String(required=True, validate=Length(equal=2))
    name = fields.String(attribute="gloss", required=True, validate=Length(min=1))


country_list_schema = CountryListSchema()


@places.route('/countries')
@places.route('/countries/<country_code>')
def read_countries(country_code=None):
    locale_id = request.args['locale']
    if country_code is None:
        result = db.session.query(Country.code, I18NValue.gloss).join(I18NKey, I18NValue).all()
        return jsonify(country_list_schema.dump(result, many=True))
    else:
        result = db.session.query(Country.code, I18NValue.gloss).filter_by(code=country_code).join(I18NKey, I18NValue).first()
        return jsonify(country_list_schema.dump(result))

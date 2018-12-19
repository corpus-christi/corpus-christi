from flask import request

from . import places
from .models import CountrySchema, Country

country_schema = CountrySchema()


@places.route('/countries')
@places.route('/countries/<country_code>')
def read_countries(country_code=None):
    locale_id = request.args['locale-id']

    if country_code is None:
        result = Country.query.all()
        return country_schema.jsonify(result, many=True)
    else:
        result = Country.query.filter_by(code=country_code).first()
        return country_schema.jsonify(result)

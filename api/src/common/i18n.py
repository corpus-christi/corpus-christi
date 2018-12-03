from flask import jsonify

from ..models import I18NLocale
from . import common


@common.route('/locales')
def index():
    result = I18NLocale.query.all()
    return jsonify({
        'id': result[0].id,
        'desc': result[0].desc
    })

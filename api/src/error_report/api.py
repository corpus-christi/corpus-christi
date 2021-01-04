from flask import request
from marshmallow import ValidationError

from . import error_report
from .models import ErrorReport, ErrorReportSchema
from .. import db
from ..shared.helpers import logged_response

error_report_schema = ErrorReportSchema()


# ---- Error report
@error_report.route('/', methods=['POST'])
def create_error_report():
    try:
        valid_error_report = error_report_schema.load(request.json)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    error_report = ErrorReport(**valid_error_report)
    db.session.add(error_report)
    db.session.commit()
    return logged_response(error_report_schema.dump(error_report), 201)

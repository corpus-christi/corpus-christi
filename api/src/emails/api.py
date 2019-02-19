import json
from datetime import datetime, timedelta

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from .models import EmailSchema
from . import emails
from .. import mail

# ---- Email

@emails.route('/', methods=['POST'])
@jwt_required
def send_email():
    # this route is intended to fail without proper credentials
    email_schema = EmailSchema()
    try:
        valid_email_request = email_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    msg = Message(valid_email_request['subject'], sender='tumissionscomputing@gmail.com', recipients=valid_email_request['recipients'])
    msg.body = valid_email_request['body']
    mail.send(msg)

    return "Sent"

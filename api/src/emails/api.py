from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from flask_mail import Message
from marshmallow import ValidationError

from . import emails
from .models import EmailSchema
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

    msg = Message(valid_email_request['subject'], recipients=valid_email_request['recipients'],
                                                  sender=valid_email_request['managerEmail'],
                                                  reply_to=valid_email_request['reply_to'],
                                                  cc=valid_email_request['cc'],
                                                  bcc=valid_email_request['bcc'])

    msg.body = valid_email_request['body']
    mail.send(msg)

    return "Sent"

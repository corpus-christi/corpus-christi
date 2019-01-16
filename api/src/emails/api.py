# ---- Email

@emails.route('/', methods=['POST'])
@jwt_required
def send_email():
    email_schema = EmailSchema()
    try:
        valid_email_request = email_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    msg = Message(valid_email_request['subject'], sender='tumissionscomputing@gmail.com', recipients=valid_email_request['recipients'])
    msg.body = valid_email_request['body']
    mail.send(msg)

    return "Sent"

from marshmallow import fields, Schema


# ---- Email Schema

class EmailSchema(Schema):
    subject = fields.String()
    body = fields.String()
    recipients = fields.List(fields.String(), required=True)
    cc = fields.List(fields.String())
    bcc = fields.List(fields.String())
    managerName = fields.String()
    managerEmail = fields.String()
    reply_to = fields.String()

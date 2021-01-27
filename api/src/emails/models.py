from marshmallow import fields, Schema
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Table

# ---- Email Model

    
    

# ---- Email Schema

class EmailSchema(Schema):
    subject = fields.String()
    body = fields.String()
    recipients = fields.List(fields.String(), required=True)
    managerName = fields.String()
    managerEmail = fields.String()
    # TODO: change the field to camelCase. Make sure UI gets updated as well
    # <2020-07-31, David Deng> #
    reply_to = fields.String()

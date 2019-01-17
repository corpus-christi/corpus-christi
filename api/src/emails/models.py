from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, DateTime, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..shared.models import StringTypes

# ---- Email Schema

class EmailSchema(Schema):
    subject = fields.String()
    body = fields.String()
    recipients = fields.List(fields.String(), required=True)
    cc = fields.List(fields.String())
    bcc = fields.List(fields.String())


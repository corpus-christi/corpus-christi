from marshmallow import fields, Schema
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from .. import db
from ..db import Base
from ..shared.models import StringTypes

# ---- Email Model

class Email(Base):
    __tablename__ = "emails_email"
    id = Column(Integer, primary_key=True)
    subject = Column(StringTypes.MEDIUM_STRING, nullable=True)
    body = Column(StringTypes.LONG_LONG_STRING, nullable=True)
    sender_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)

    person = relationship('Recipient', back_populates='emails', lazy=True)

    def __repr__(self):
        return f"<Email(id={self.id})>"
    

# ---- Email Schema

class EmailSchema(Schema):
    subject = fields.String()
    body = fields.String()
    recipients = fields.List(fields.String(), required=True)
    managerName = fields.String()
    managerEmail = fields.String()
    recipientIds = fields.List(fields.Integer(), required=True)
    senderId = fields.Integer()
    # TODO: change the field to camelCase. Make sure UI gets updated as well
    # <2020-07-31, David Deng> #
    reply_to = fields.String()

class Recipient(Base):
    __tablename__ = 'emails_recipients'
    person_id =Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    email_id = Column(Integer, ForeignKey('emails_email.id'), primary_key=True)

    emails = relationship("Email", back_populates='person')
    person = relationship("Person", back_populates='emails')

class RecipientSchema(Schema):
    emails = fields.Nested('EmailSchema', dump_only=True)
    person = fields.Nested('PersonSchema', dump_only=True)

    person_id = fields.Integer(required = True, min=1)
    email_id = fields.Integer(required = True, min=1)

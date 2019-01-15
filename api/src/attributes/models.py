from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..places.models import Location
from ..shared.models import StringTypes


# ---- Attribute

class Attribute(Base):
    __tablename__ = 'people_attributes'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.LOCALE_CODE)
    type_i18n = Column(StringTypes.LOCALE_CODE)
    seq = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)

    enumerated_values = relationship(
        'Enumerated_Value', backref='attribute', lazy=True)

    def __repr__(self):
        return f"<Attribute(id={self.id})>"


class AttributeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    type_i18n = fields.String(data_key='typeI18n')
    seq = fields.Integer(required=True)
    active = fields.Boolean(required=True)

    enumerated_values = fields.Nested('Enumerated_ValueSchema', many=True)

# ---- Enumerated_Value


class Enumerated_Value(Base):
    __tablename__ = 'people_enumerated_value'
    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey('people_attributes.id'))
    value_i18n = Column(StringTypes.LOCALE_CODE)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Enumerated_Value(id={self.id})>"


class Enumerated_ValueSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    attribute_id = fields.Integer(data_key='attributeId')
    value_i18n = fields.String(data_key='valueI18n')
    active = fields.Boolean(required=True)

# ---- Person-Attribute


class Person_Attribute(Base):
    __tablename__ = 'people_person_attributes'
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)
    attribute_id = Column(Integer, ForeignKey(
        'people_attributes.id'), primary_key=True)
    enum_value_id = Column(Integer, ForeignKey('people_enumerated_value.id'))
    string_value = Column(StringTypes.LOCALE_CODE)
    person = relationship('Person', backref='person_attributes', lazy=True)
    attribute = relationship(
        'Attribute', backref='person_attributes', lazy=True)
    enumerated_values = relationship(
        'Enumerated_Value', backref='person_attributes', lazy=True)

    def __repr__(self):
        return f"<Person-Attribute(person_id={self.person_id},attribute_id={self.attribute_id})>"


class Person_AttributeSchema(Schema):
    person_id = fields.Integer(
        dump_only=True, data_key='personId', required=True)
    attribute_id = fields.Integer(
        dump_only=False, data_key='attributeId', required=True)
    enum_value_id = fields.Integer(data_key='enumValueId')
    string_value = fields.String(data_key='stringValue')

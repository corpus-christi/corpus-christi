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
    name_i18n = Column(StringTypes.LOCALE_CODE, ForeignKey('i18n_key.id'))
    type_i18n = Column(StringTypes.LOCALE_CODE, ForeignKey('i18n_key.id'))
    seq = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)
    enumerated_types_list = ['attribute.radio',
                             'attribute.check', 'attribute.dropdown']
    nonenumerated_types_list = [
        'attribute.float', 'attribute.integer', 'attribute.string', 'attribute.date']

    enumerated_values = relationship(
        'EnumeratedValue', backref='attribute', lazy=True)

    def __repr__(self):
        return f"<Attribute(id={self.id})>"

    @staticmethod
    def available_types():
        return Attribute.enumerated_types_list + Attribute.nonenumerated_types_list


class AttributeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    type_i18n = fields.String(data_key='typeI18n')
    seq = fields.Integer(required=True)
    active = fields.Boolean(required=True)

    enumerated_values = fields.Nested('EnumeratedValueSchema', many=True)

# ---- EnumeratedValue


class EnumeratedValue(Base):
    __tablename__ = 'people_enumerated_value'
    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey('people_attributes.id'))
    value_i18n = Column(StringTypes.LOCALE_CODE, ForeignKey('i18n_key.id'))
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<EnumeratedValue(id={self.id})>"


class EnumeratedValueSchema(Schema):
    id = fields.Integer(dump_only=False, required=True, validate=Range(min=1))
    attribute_id = fields.Integer(data_key='attributeId')
    value_i18n = fields.String(data_key='valueI18n')
    active = fields.Boolean(required=True)

# ---- Person-Attribute


class PersonAttribute(Base):
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
        'EnumeratedValue', backref='person_attributes', lazy=True)

    def __repr__(self):
        return f"<Person-Attribute(person_id={self.person_id},attribute_id={self.attribute_id})>"


class PersonAttributeSchema(Schema):
    person_id = fields.Integer(
        dump_only=True, data_key='personId', required=True)
    attribute_id = fields.Integer(
        dump_only=True, data_key='attributeId', required=True)
    enum_value_id = fields.Integer(data_key='enumValueId')
    string_value = fields.String(data_key='stringValue')

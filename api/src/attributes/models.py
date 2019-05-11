import os
import json

from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from .. import db
from src.i18n.models import i18n_create, I18NLocale
from ..places.models import Location
from ..shared.models import StringTypes


# ---- Attribute

class Attribute(Base):
    __tablename__ = 'people_attributes'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.I18N_KEY)
    type_i18n = Column(StringTypes.I18N_KEY)
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

    @classmethod
    def load_types_from_file(cls, file_name='attribute_types.json'):
        count = 0
        file_path = os.path.abspath(os.path.join(
            __file__, os.path.pardir, 'data', file_name))

        with open(file_path, 'r') as fp:

            attribute_types = json.load(fp)

            for attribute_type in attribute_types:
                attribute_name = attribute_type['name']
                name_i18n = f'attribute.{attribute_name}'

                for locale in attribute_type['locales']:
                    locale_code = locale['locale_code']
                    if not db.session.query(I18NLocale).get(locale_code):
                        db.session.add(I18NLocale(code=locale_code, desc=''))
                    i18n_create(name_i18n, locale['locale_code'],
                                locale['name'], description=f"Attribute type {attribute_name}")
                count += 1
            db.session.commit()
            fp.close()
            return count


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
    value_i18n = Column(StringTypes.I18N_KEY)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<EnumeratedValue(id={self.id})>"


class EnumeratedValueSchema(Schema):
    id = fields.Integer(required=True, validate=Range(min=1))
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
    enum_value_id = Column(Integer, ForeignKey('people_enumerated_value.id'), nullable=True)
    string_value = Column(StringTypes.LONG_STRING)
    person = relationship('Person', backref='person_attributes', lazy=True)
    attribute = relationship(
        'Attribute', backref='person_attributes', lazy=True)
    enumerated_values = relationship(
        'EnumeratedValue', backref='person_attributes', lazy=True)

    def __repr__(self):
        return f"<Person-Attribute(person_id={self.person_id},attribute_id={self.attribute_id})>"


class PersonAttributeSchema(Schema):
    person_id = fields.Integer(data_key='personId', required=True)
    attribute_id = fields.Integer(data_key='attributeId', required=True)
    enum_value_id = fields.Integer(data_key='enumValueId', allow_none=True)
    string_value = fields.String(data_key='stringValue')

from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..places.models import Location
from ..shared.models import StringTypes


# ---- Person

class Person(Base):
    __tablename__ = 'people_person'
    id = Column(Integer, primary_key=True)
    first_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    last_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    gender = Column(String(1))
    birthday = Column(Date)
    phone = Column(StringTypes.MEDIUM_STRING)
    email = Column(StringTypes.MEDIUM_STRING)
    location_id = Column(Integer, ForeignKey('places_location.id'))

    address = relationship(Location, backref='people', lazy=True)

    def __repr__(self):
        return f"<Person(id={self.id},name='{self.first_name} {self.last_name}')>"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PersonSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    first_name = fields.String(data_key='firstName', required=True, validate=Length(min=1))
    last_name = fields.String(data_key='lastName', required=True, validate=Length(min=1))
    gender = fields.String(validate=OneOf(['M', 'F']))
    birthday = fields.Date()
    phone = fields.String()
    email = fields.String()


# ---- Account

class Account(Base):
    __tablename__ = 'people_account'
    id = Column(Integer, primary_key=True)
    username = Column(StringTypes.MEDIUM_STRING, nullable=False, unique=True)
    password_hash = Column(StringTypes.PASSWORD_HASH, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)

    # One-to-one relationship; see https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-one
    person = relationship("Person", backref=backref("account", uselist=False))

    def __repr__(self):
        return "<Account(id={},username='{}',person='{}:{}')>" \
            .format(self.id, self.username, self.person.id, self.person.full_name())

    # From Flask Web Dev book
    @property
    def password(self):
        """Hashed passwords are 'write-only'."""
        raise AttributeError("Can't read hashed password")

    @password.setter
    def password(self, password):
        """Hash the plain-text password on the way into the database."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check that the hashed password matches a user-supplied plaint-text one."""
        return check_password_hash(self.password_hash, password)


class AccountSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    username = fields.String(required=True, validate=Length(min=1))
    password = fields.String(attribute='password_hash', load_only=True,
                             required=True, validate=Length(min=6))
    active = fields.Boolean()
    person_id = fields.Integer(required=True, data_key="personId", validate=Range(min=1))

    @pre_load
    def hash_password(self, data):
        """Make sure the password is properly hashed when creating a new account."""
        data['password'] = generate_password_hash(data['password'])
        return data

# ---- Attribute

class Attribute(Base):
    __tablename__ = 'people_attributes'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.LOCALE_CODE)
    type_i18n = Column(StringTypes.LOCALE_CODE)
    seq = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Attribute(id={self.id})>"
    

class AttributeSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     name_i18n = fields.String(data_key='nameI18n')
     type_i18n = fields.String(data_key='typeI18n')
     seq = fields.Integer(required=True)
     active = fields.Boolean(required=True)

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
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    attribute_id = Column(Integer, ForeignKey('people_attributes.id'), primary_key=True)
    enum_value_id = Column(Integer, ForeignKey('people_enumerated_value.id'))
    string_value = Column(StringTypes.LOCALE_CODE)
    person = relationship('Person', backref='person_attributes', lazy=True)
    attribute = relationship('Attribute', backref='person_attributes', lazy=True)
    enumerated_values = relationship('Enumerated_Value', backref='person_attributes', lazy=True)

    def __repr__(self):
        return f"<Person-Attribute(person_id={self.person_id},attribute_id={self.attribute_id})>"


class Person_AttributeSchema(Schema):
     person_id = fields.Integer(dump_only=True, data_key='personId', required=True)
     attribute_id = fields.Integer(dump_only=True, data_key='attributeId', required=True)
     enum_value_id = fields.Integer(data_key='enumValueId')
     string_value = fields.String(data_key='stringValue')


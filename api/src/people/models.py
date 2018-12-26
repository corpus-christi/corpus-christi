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
    username = Column(StringTypes.MEDIUM_STRING, nullable=False)
    password_hash = Column(StringTypes.PASSWORD_HASH, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)

    # One-to-one relationship; see https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-one
    person = relationship("Person", backref=backref("account", uselist=False))

    def __repr__(self):
        return "<Account(id={},person_id={},person='{} {}')>" \
            .format(self.id, self.person.id, self.person.first_name, self.person.last_name)

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

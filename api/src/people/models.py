import os

from flask import json
from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from src.i18n.models import i18n_create, I18NLocale
from .. import db
from ..places.models import Location
from ..shared.models import StringTypes


# ---- Person

class Person(Base):
    __tablename__ = 'people_person'
    id = Column(Integer, primary_key=True)
    first_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    last_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    second_last_name = Column(StringTypes.MEDIUM_STRING, nullable=True)
    gender = Column(String(1))
    birthday = Column(Date)
    phone = Column(StringTypes.MEDIUM_STRING)
    email = Column(StringTypes.MEDIUM_STRING)
    active = Column(Boolean, nullable=False, default=True)
    location_id = Column(Integer, ForeignKey('places_location.id'), nullable=True, default=None)

    address = relationship(Location, backref='people', lazy=True)
    # events_per refers to the events led by the person (linked via events_eventperson table)
    events_per = relationship("EventPerson", back_populates="person")
    # events_par refers to the participated events (linked via events_eventparticipant table)
    events_par = relationship("EventParticipant", back_populates="person")
    teams = relationship("TeamMember", back_populates="member")
    diplomas_awarded = relationship('DiplomaAwarded', back_populates='students', lazy=True, uselist=True)
    members = relationship('Member', back_populates='person', lazy=True)
    images = relationship('ImagePerson', back_populates='person')

    def _init(self, accountInfo):
        self.accountInfo = accountInfo

    def __repr__(self):
        return f"<Person(id={self.id},name='{self.first_name} {self.last_name}')>"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PersonSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    first_name = fields.String(
        data_key='firstName', required=True, validate=Length(min=1))
    last_name = fields.String(
        data_key='lastName', required=True, validate=Length(min=1))
    second_last_name = fields.String(
        data_key='secondLastName', allow_none=True)
    gender = fields.String(validate=OneOf(['M', 'F']), allow_none=True)
    birthday = fields.Date(allow_none=True)
    phone = fields.String(allow_none=True)
    email = fields.String(allow_none=True)

    active = fields.Boolean(required=True)
    location_id = fields.Integer(data_key='locationId', allow_none=True)

    accountInfo = fields.Nested(
        'AccountSchema', allow_none=True, only=['username', 'id', 'active', 'roles'])

    attributesInfo = fields.Nested('PersonAttributeSchema', many=True)
    images = fields.Nested('ImagePersonSchema', many=True, exclude=['person'], dump_only=True)


# Defines join table for people_account and people_role


people_account_role = Table('account_role', Base.metadata,
                            Column('people_account_id', Integer, ForeignKey(
                                'people_account.id'), primary_key=True),
                            Column('people_role_id', Integer, ForeignKey(
                                'people_role.id'), primary_key=True)
                            )

# ---- Account


class Account(Base):
    __tablename__ = 'people_account'
    id = Column(Integer, primary_key=True)
    username = Column(StringTypes.MEDIUM_STRING, nullable=False, unique=True)
    password_hash = Column(StringTypes.PASSWORD_HASH, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    confirmed = Column(Boolean, nullable=False, default=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)

    # One-to-one relationship; see https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-one
    person = relationship("Person", backref=backref("account", uselist=False))
    roles = relationship("Role",
                         secondary=people_account_role, backref="accounts")

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
    active = fields.Boolean(missing=None)
    confirmed = fields.Boolean()
    person_id = fields.Integer(
        required=True, data_key="personId", validate=Range(min=1))
    roles = fields.Nested('RoleSchema', many=True)

    @pre_load
    def hash_password(self, data):
        """Make sure the password is properly hashed when creating a new account."""
        if 'password' in data.keys():
            data['password'] = generate_password_hash(data['password'])
        return data


# ---- Role

class Role(Base):
    __tablename__ = 'people_role'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.I18N_KEY)
    active = Column(Boolean)

    def __repr__(self):
        return f"<Role(id={self.id})>"

    @classmethod
    def load_from_file(cls, file_name='roles.json'):
        count = 0
        file_path = os.path.abspath(os.path.join(
            __file__, os.path.pardir, 'data', file_name))

        with open(file_path, 'r') as fp:
            if db.session.query(Role).count() == 0:

                roles = json.load(fp)

                for role in roles:
                    role_name = role['name']
                    name_i18n = f'role.{role_name}'

                    for locale in role['locales']:
                        locale_code = locale['locale_code']
                        if not db.session.query(I18NLocale).get(locale_code):
                            db.session.add(I18NLocale(
                                code=locale_code, desc=''))
                        i18n_create(name_i18n, locale['locale_code'],
                                    locale['name'], description=f"Role {role_name}")
                    db.session.add(
                        cls(name_i18n=name_i18n, active=True))
                    count += 1
                db.session.commit()
            fp.close()
            return count

        # return 0


class RoleSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    active = fields.Boolean()


# ---- Manager

class Manager(Base):
    __tablename__ = 'people_manager'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('people_manager.id'))
    description_i18n = Column(StringTypes.I18N_KEY,
                              ForeignKey('i18n_key.id'), nullable=False)
    manager = relationship('Manager', backref='subordinates',
                           lazy=True, remote_side=[id])
    groups = relationship('Group', back_populates='manager', lazy=True)
    person = relationship("Person", backref=backref("manager", uselist=False))

    def __repr__(self):
        return f"<Manager(id={self.id})>"


class ManagerSchema(Schema):
    id = fields.Integer(dump_only=True, data_key='id',
                        required=True, validate=Range(min=1))
    person_id = fields.Integer(
        data_key='person_id', required=True, validate=Range(min=1))
    manager_id = fields.Integer(data_key='manager_id', validate=Range(min=1))
    description_i18n = fields.String(
        data_key='description_i18n', required=True)
    person = fields.Nested('PersonSchema', dump_only=True)

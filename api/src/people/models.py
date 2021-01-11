import os

from flask import json
from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from ..db import Base
from ..i18n.models import i18n_create, I18NLocale
from ..shared.models import StringTypes

# Defines join table for people_person and people_role
people_person_role = Table('person_role', Base.metadata,
                           Column('people_person_id', Integer, ForeignKey(
                               'people_person.id'), primary_key=True),
                           Column('id', Integer, ForeignKey(
                               'people_role.id'), primary_key=True)
                           )


# ---- Person


class Person(Base):
    __tablename__ = 'people_person'
    id = Column(Integer, primary_key=True)

    # Personal info
    first_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    last_name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    second_last_name = Column(StringTypes.MEDIUM_STRING, nullable=True)
    gender = Column(String(1))
    birthday = Column(Date)
    phone = Column(StringTypes.MEDIUM_STRING)
    email = Column(StringTypes.MEDIUM_STRING)

    # Account info
    username = Column(StringTypes.MEDIUM_STRING, nullable=False, unique=True)
    password_hash = Column(StringTypes.PASSWORD_HASH, nullable=False)
    confirmed = Column(Boolean, nullable=True, default=0)

    active = Column(Boolean, nullable=False, default=True)
    address_id = Column(
        Integer,
        ForeignKey('places_address.id'),
        nullable=True,
        default=None)

    address = relationship('Address', back_populates='people', lazy=True)
    # events_per refers to the events led by the person (linked via
    # events_eventperson table)
    events_per = relationship("EventPerson", back_populates="person")
    # events_par refers to the participated events (linked via
    # events_eventparticipant table)
    events_par = relationship("EventParticipant", back_populates="person")
    teams = relationship("TeamMember", back_populates="member")
    diplomas_awarded = relationship(
        'DiplomaAwarded',
        back_populates='students',
        lazy=True,
        uselist=True)
    members = relationship('Member', back_populates='person', lazy=True)
    member_histories = relationship(
        'MemberHistory',
        back_populates='person',
        lazy=True)
    managers = relationship('Manager', back_populates='person', lazy=True)
    images = relationship('ImagePerson', back_populates='person')
    teacher = relationship('ClassMeeting', back_populates='person', lazy=True)
    students = relationship('Student', back_populates='person', lazy=True)
    roles = relationship(
        "Role",
        secondary=people_person_role,
        back_populates="persons")
    completions = relationship(
        'CourseCompletion',
        back_populates='people',
        lazy=True)
    person_attributes = relationship(
        'PersonAttribute',
        back_populates='person',
        lazy=True)
    attendances = relationship(
        'Attendance',
        back_populates='person',
        lazy=True)

    def __repr__(self):
        return f"<Person(id={self.id},name='{self.first_name} {self.last_name}')>"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

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


class PersonSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))

    first_name = fields.String(
        data_key='firstName',
        required=True,
        validate=Length(
            min=1))
    last_name = fields.String(
        data_key='lastName',
        required=True,
        validate=Length(
            min=1))
    second_last_name = fields.String(
        data_key='secondLastName', allow_none=True)
    gender = fields.String(validate=OneOf(['M', 'F']), allow_none=True)
    birthday = fields.Date(allow_none=True)
    phone = fields.String(allow_none=True)
    email = fields.String(allow_none=True)

    username = fields.String(required=True, validate=Length(min=1))
    password = fields.String(
        attribute='password_hash',
        load_only=True,
        required=True,
        validate=Length(
            min=6))
    confirmed = fields.Boolean(dump_only=True)

    active = fields.Boolean(required=True)
    address_id = fields.Integer(data_key='addressId', allow_none=True)

    attributesInfo = fields.Nested('PersonAttributeSchema', many=True)
    images = fields.Nested(
        'ImagePersonSchema',
        many=True,
        exclude=['person'],
        dump_only=True)
    roles = fields.Nested('RoleSchema', many=True, dump_only=True)
    members = fields.Nested(
        'MemberSchema',
        only=[
            'group_id',
            'active'],
        many=True,
        dump_only=True)
    managers = fields.Nested(
        'ManagerSchema',
        only=[
            'group_id',
            'active'],
        many=True,
        dump_only=True)
    member_histories = fields.Nested(
        'MemberHistorySchema',
        many=True,
        dump_only=True,
        data_key='memberHistories',
        only=(
            'id',
            'time',
            'is_join',
            'group_id'))

    @pre_load
    def hash_password(self, data, **kwargs):
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
    persons = relationship(
        "Person",
        secondary=people_person_role,
        back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id})>"

    @classmethod
    def load_from_file(cls, file_name='roles.json'):
        count = 0
        file_path = os.path.abspath(
            os.path.join(
                __file__,
                os.path.pardir,
                'data',
                file_name))

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
                        i18n_create(
                            name_i18n,
                            locale['locale_code'],
                            locale['name'],
                            description=f"Role {role_name}")
                    db.session.add(
                        cls(name_i18n=name_i18n, active=True))
                    count += 1
                db.session.commit()
            fp.close()
            return count
        return 0


class RoleSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    active = fields.Boolean()

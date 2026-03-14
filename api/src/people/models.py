import os
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column, backref
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from ..db import Base, SessionLocal
from ..places.models import Address
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Personal info
    first_name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    last_name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    second_last_name: Mapped[Optional[str]] = mapped_column(StringTypes.MEDIUM_STRING, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(1))
    birthday: Mapped[Optional[Date]] = mapped_column(Date)
    phone: Mapped[Optional[str]] = mapped_column(StringTypes.MEDIUM_STRING)
    email: Mapped[Optional[str]] = mapped_column(StringTypes.MEDIUM_STRING)

    # Account info
    username: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(StringTypes.PASSWORD_HASH, nullable=False)
    confirmed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=0)

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    address_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('places_address.id'), nullable=True, default=None)

    address = relationship(Address, backref='people', lazy=True)
    events_per = relationship("EventPerson", back_populates="person")
    events_par = relationship("EventParticipant", back_populates="person")
    teams = relationship("TeamMember", back_populates="member")
    diplomas_awarded = relationship('DiplomaAwarded', back_populates='students', lazy=True, uselist=True)
    members = relationship('Member', back_populates='person', lazy=True)
    images = relationship('ImagePerson', back_populates='person')

    roles = relationship("Role", secondary=people_person_role, backref="person")

    def __repr__(self):
        return f"<Person(id={self.id},name='{self.first_name} {self.last_name}')>"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def password(self):
        raise AttributeError("Can't read hashed password")

    @password.setter
    def password(self, password):
        self.password_hash = _pwd_context.hash(password)

    def verify_password(self, password):
        return _pwd_context.verify(password, self.password_hash)


# Pydantic schemas for Person
class PersonBase(BaseModel):
    firstName: str = Field(alias='first_name')
    lastName: str = Field(alias='last_name')
    secondLastName: Optional[str] = Field(None, alias='second_last_name')
    gender: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    username: str
    active: bool = True
    addressId: Optional[int] = Field(None, alias='address_id')

    model_config = ConfigDict(populate_by_name=True)


class PersonCreate(PersonBase):
    password: str


class PersonUpdate(BaseModel):
    firstName: Optional[str] = Field(None, alias='first_name')
    lastName: Optional[str] = Field(None, alias='last_name')
    secondLastName: Optional[str] = Field(None, alias='second_last_name')
    gender: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None
    addressId: Optional[int] = Field(None, alias='address_id')

    model_config = ConfigDict(populate_by_name=True)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nameI18n: Optional[str] = Field(None, alias='name_i18n')
    active: Optional[bool] = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    firstName: str = Field(alias='first_name')
    lastName: str = Field(alias='last_name')
    secondLastName: Optional[str] = Field(None, alias='second_last_name')
    gender: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    username: str
    confirmed: Optional[bool] = None
    active: bool
    addressId: Optional[int] = Field(None, alias='address_id')
    roles: List[RoleRead] = []


# Keep marshmallow-style Schema for backward compatibility with commands
class PersonSchema:
    """Compatibility shim for marshmallow-style dumps in commands."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'firstName': obj.first_name,
            'lastName': obj.last_name,
            'secondLastName': obj.second_last_name,
            'gender': obj.gender,
            'birthday': str(obj.birthday) if obj.birthday else None,
            'phone': obj.phone,
            'email': obj.email,
            'username': obj.username,
            'confirmed': obj.confirmed,
            'active': obj.active,
            'addressId': obj.address_id,
        }


# ---- Role

class Role(Base):
    __tablename__ = 'people_role'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_i18n: Mapped[Optional[str]] = mapped_column(StringTypes.I18N_KEY)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self):
        return f"<Role(id={self.id})>"

    @classmethod
    def load_from_file(cls, file_name='roles.json'):
        import json
        from ..i18n.models import i18n_create, I18NLocale
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        with SessionLocal() as db:
            from sqlalchemy import select
            if db.execute(select(cls)).scalars().first() is None:
                with open(file_path, 'r') as fp:
                    roles = json.load(fp)

                    for role in roles:
                        role_name = role['name']
                        name_i18n = f'role.{role_name}'

                        for locale in role['locales']:
                            locale_code = locale['locale_code']
                            if not db.get(I18NLocale, locale_code):
                                db.add(I18NLocale(code=locale_code, desc=''))
                            i18n_create(db, name_i18n, locale['locale_code'],
                                        locale['name'], description=f"Role {role_name}")
                        db.add(cls(name_i18n=name_i18n, active=True))
                        count += 1
                    db.commit()
        return count


class RoleSchema:
    """Compatibility shim for marshmallow-style dumps."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'nameI18n': obj.name_i18n,
            'active': obj.active,
        }


# ---- Manager

class Manager(Base):
    __tablename__ = 'people_manager'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), nullable=False)
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('people_manager.id'))
    description_i18n: Mapped[str] = mapped_column(StringTypes.I18N_KEY, ForeignKey('i18n_key.id'), nullable=False)
    manager = relationship('Manager', backref='subordinates', lazy=True, remote_side=[id])
    groups = relationship('Group', back_populates='manager', lazy=True)
    person = relationship("Person", backref=backref("manager", uselist=False))

    def __repr__(self):
        return f"<Manager(id={self.id})>"


class ManagerCreate(BaseModel):
    person_id: int
    manager_id: Optional[int] = None
    description_i18n: str


class ManagerRead(ManagerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ManagerSchema:
    """Compatibility shim for marshmallow-style dumps."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        result = {
            'id': obj.id,
            'person_id': obj.person_id,
            'manager_id': obj.manager_id,
            'description_i18n': obj.description_i18n,
        }
        if hasattr(obj, 'person') and obj.person:
            result['person'] = PersonSchema()._dump_one(obj.person)
        return result

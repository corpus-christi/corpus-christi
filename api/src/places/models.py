import os

from flask import json
from marshmallow import Schema, fields
from marshmallow.validate import Length, Range
from sqlalchemy import Column, String, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship

from .. import db
from ..db import Base
from ..i18n.models import I18NKey
from ..shared.helpers import get_or_create
from ..shared.models import StringTypes


# ---- Country

class Country(Base):
    """Country; uses ISO 3166-1 country codes"""
    __tablename__ = 'places_country'
    code = Column(String(2), primary_key=True)
    name_i18n = Column(
        StringTypes.I18N_KEY,
        ForeignKey('i18n_key.id'),
        nullable=False)
    key = relationship('I18NKey', back_populates='countries', lazy=True)
    addresses = relationship('Address', back_populates='country', lazy=True)
    areas = relationship('Area', back_populates='country', lazy=True)

    def __repr__(self):
        return f"<Country(code={self.code},i18n_key='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='country-codes.json'):
        count = 0
        file_path = os.path.abspath(
            os.path.join(
                __file__,
                os.path.pardir,
                'data',
                file_name))

        with open(file_path, 'r') as fp:
            countries = json.load(fp)

            for country in countries:
                country_code = country['Code']
                country_name = country['Name']

                name_i18n = f'country.name.{country_code}'

                # Create the key if it does not exist

                get_or_create(db.session, I18NKey, filters={
                    'id': name_i18n}, attributes={
                    'desc': f"Country {country_name}"})

                # Note: Create I18NValue s with flask i18n load <locale>

                # Add to the Country table.
                if not db.session.query(cls).filter_by(
                        code=country_code).count():
                    db.session.add(cls(code=country_code, name_i18n=name_i18n))
                    count += 1
            db.session.commit()
        fp.close()
        return count


class CountrySchema(Schema):
    code = fields.String()
    name_i18n = fields.String()


# ---- Area


class Area(Base):
    """Generic area within country (e.g., state, province)"""
    __tablename__ = 'places_area'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    country_code = Column(String(2), ForeignKey(
        'places_country.code'), nullable=False)

    addresses = relationship('Address', back_populates='areas')
    country = relationship('Country', back_populates='areas', lazy=True)
    active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Area(name={self.name},Country Code='{self.country_code}')>"


class AreaSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    country_code = fields.String(required=True, validate=Length(min=1))
    active = fields.Boolean(missing=1)
    country = fields.Nested('CountrySchema')


# ---- Location

class Location(Base):
    __tablename__ = 'places_location'
    id = Column(Integer, primary_key=True, nullable=False)
    description = Column(StringTypes.MEDIUM_STRING)
    address_id = Column(Integer, ForeignKey(
        'places_address.id'), nullable=False)
    address = relationship('Address', back_populates='locations', lazy=True)
    events = relationship('Event', back_populates="location")
    assets = relationship('Asset', back_populates="location")
    images = relationship('ImageLocation', back_populates="location")
    active = Column(Boolean, nullable=False, default=True)
    meeting_location = relationship(
        'ClassMeeting',
        back_populates='locations',
        lazy=True)

    def __repr__(self):
        attributes = [f"id='{self.id}'"]
        for attr in ['description', "address_id"]:
            if hasattr(self, attr):
                value = getattr(self, attr)
                attributes.append(f"{attr}={value}")
        as_string = ",".join(attributes)
        return f"<Location({as_string})>"


class LocationSchema(Schema):
    id = fields.Integer(dump_only=True, required=False, validate=Range(min=1))
    description = fields.String(required=False)
    address_id = fields.Integer(required=True, validate=Range(min=1))
    active = fields.Boolean(missing=1)
    address = fields.Nested('AddressSchema')


# ---- Address


class Address(Base):
    __tablename__ = 'places_address'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    address = Column(StringTypes.LONG_STRING, nullable=False)
    city = Column(StringTypes.MEDIUM_STRING, nullable=False)
    area_id = Column(Integer, ForeignKey(
        'places_area.id', ondelete='CASCADE'), nullable=False)
    country_code = Column(StringTypes.SHORT_STRING, ForeignKey(
        'places_country.code'), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    country = relationship('Country', back_populates='addresses', lazy=True)
    meetings = relationship('Meeting', back_populates='address', lazy=True)
    locations = relationship('Location', back_populates='address', lazy=True)
    active = Column(Boolean, nullable=False, default=True)
    people = relationship('Person', back_populates='address', lazy=True)
    areas = relationship('Area', back_populates='addresses')

    def __repr__(self):
        attributes = [f"id='{self.id}'"]
        for attr in ['name', 'address', 'city', 'area_id', 'country_code', 'latitude', 'longitude']:
            if hasattr(self, attr):
                value = getattr(self, attr)
                attributes.append(f"{attr}={value}")
        as_string = ",".join(attributes)
        return f"<Address({as_string})>"


class AddressSchema(Schema):
    id = fields.Integer(dump_only=True, required=False, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    address = fields.String(required=True, validate=Length(min=1))
    city = fields.String(required=True, validate=Length(min=1))
    area_id = fields.Integer(required=True, validate=Range(min=1))
    country_code = fields.String(required=True)
    latitude = fields.Float()
    longitude = fields.Float()
    active = fields.Boolean(missing=1)
    area = fields.Nested('AreaSchema')
    country = fields.Nested('CountrySchema')

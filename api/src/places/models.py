import os

from flask import json
from marshmallow import Schema, fields
from marshmallow.validate import Length, Range
from sqlalchemy import Column, String, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship

from src.db import Base
from src.i18n.models import i18n_create, I18NLocale
from .. import db
from ..shared.models import StringTypes


# ---- Country

class Country(Base):
    """Country; uses ISO 3166-1 country codes"""
    __tablename__ = 'places_country'
    code = Column(String(2), primary_key=True)
    name_i18n = Column(StringTypes.I18N_KEY, ForeignKey('i18n_key.id'), nullable=False)
    key = relationship('I18NKey', backref='countries', lazy=True)

    def __repr__(self):
        return f"<Country(code={self.code},i18n_key='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='country-codes.json', locale_code='en-US'):
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        if not db.session.query(I18NLocale).get(locale_code):
            db.session.add(I18NLocale(code=locale_code, desc='English US'))

        with open(file_path, 'r') as fp:
            countries = json.load(fp)

            for country in countries:
                country_code = country['Code']
                country_name = country['Name']

                name_i18n = f'country.name.{country_code}'
                i18n_create(name_i18n, locale_code,
                            country_name, description=f"Country {country_name}")

                db.session.add(cls(code=country_code, name_i18n=name_i18n))
                count += 1
            db.session.commit()
        return count


# ---- Area

class Area(Base):
    """Generic area within country (e.g., state, province)"""
    __tablename__ = 'places_area'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    country_code = Column(String(2), ForeignKey('places_country.code'), nullable=False)

    country = relationship(Country, backref='areas', lazy=True)


class AreaSchema(Schema):
    id = fields.Integer(required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    country_id = fields.Integer(required=True, validate=Range(min=1))


# ---- Location

class Location(Base):
    __tablename__ = 'places_location'
    id = Column(Integer, primary_key=True)
    address = Column(StringTypes.LONG_STRING)
    city = Column(StringTypes.MEDIUM_STRING)
    area_id = Column(Integer, ForeignKey('places_area.id'))
    country_code = Column(String(2), ForeignKey('places_country.code'))
    latitude = Column(Float)
    longitude = Column(Float)

    area = relationship(Area, backref='locations', lazy=True)
    country = relationship(Country, backref='locations', lazy=True)
    events = relationship('Event', back_populates="location")
    assets = relationship('Asset', back_populates="location")


    def __repr__(self):
        attributes = [f"id='{self.id}'"]
        for attr in ['address', 'city', 'area_id', 'country_id', 'latitude', 'longitude']:
            if hasattr(self, attr):
                attributes.append(f"{attr}={self.attr}")
        as_string = ",".join(attributes)
        return f"<Location({as_string})>"


class LocationSchema(Schema):
    id = fields.Integer(required=True, validate=Range(min=1))
    address = fields.String()
    city = fields.String()
    area_id = fields.Integer(validate=Range(min=1))
    country_code = fields.String()
    latitude = fields.Float()
    longitude = fields.Float()

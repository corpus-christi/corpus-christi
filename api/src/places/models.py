import os

from flask import json
from flask_marshmallow import Schema
from marshmallow import fields
from marshmallow.validate import Length, Range

from src.i18n.models import i18n_create, I18NLocale
from .. import orm
from ..shared.models import StringTypes


# ---- Country

class Country(orm.Model):
    """Country; uses ISO 3166-1 country codes"""
    __tablename__ = 'places_country'
    code = orm.Column(orm.String(2), primary_key=True)
    name_i18n = orm.Column(StringTypes.I18N_KEY, orm.ForeignKey('i18n_key.id'), nullable=False)
    key = orm.relationship('I18NKey', backref='countries', lazy=True)

    def __repr__(self):
        return f"<Country(id={self.id},i18n_key='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='country-codes.json', locale_code='en-US'):
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        orm.session.add(I18NLocale(code=locale_code, desc='English US'))

        with open(file_path, 'r') as fp:
            countries = json.load(fp)

            for country in countries:
                country_code = country['Code']
                country_name = country['Name']

                name_i18n = f'country.name.{country_code}'
                i18n_create(name_i18n, locale_code,
                            country_name, description=f"Name of {country_name}")

                orm.session.add(cls(code=country_code, name_i18n=name_i18n))
                count += 1
            orm.session.commit()
        return count


class CountrySchema(Schema):
    code = fields.String(required=True, validate=Length(min=1))
    name_i18n = fields.String(required=True, validate=Length(min=1))


# ---- Area

class Area(orm.Model):
    """Generic area within country (e.g., state, province)"""
    __tablename__ = 'places_area'
    id = orm.Column(orm.Integer, primary_key=True)
    name = orm.Column(StringTypes.MEDIUM_STRING, nullable=False)
    country_code = orm.Column(orm.String(2), orm.ForeignKey('places_country.code'), nullable=False)

    country = orm.relationship(Country, backref='areas', lazy=True)


class AreaSchema(Schema):
    id = fields.Integer(required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    country_id = fields.Integer(required=True, validate=Range(min=1))


# ---- Location

class Location(orm.Model):
    __tablename__ = 'places_location'
    id = orm.Column(orm.Integer, primary_key=True)
    address = orm.Column(StringTypes.LONG_STRING)
    city = orm.Column(StringTypes.MEDIUM_STRING)
    area_id = orm.Column(orm.Integer, orm.ForeignKey('places_area.id'))
    country_id = orm.Column(orm.Integer, orm.ForeignKey('places_country.code'))
    latitude = orm.Column(orm.Float)
    longitude = orm.Column(orm.Float)

    area = orm.relationship(Area, backref='locations', lazy=True)
    country = orm.relationship(Country, backref='locations', lazy=True)

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
    country_id = fields.Integer(validate=Range(min=1))
    latitude = fields.Float()
    longitude = fields.Float()

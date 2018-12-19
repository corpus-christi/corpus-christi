from flask_marshmallow import Schema
from marshmallow import fields
from marshmallow.validate import Length, Range, OneOf

from .. import orm
from ..places.models import Location
from ..shared.models import StringTypes


# ---- Person

class Person(orm.Model):
    __tablename__ = 'people_person'
    id = orm.Column(orm.Integer, primary_key=True)
    first_name = orm.Column(StringTypes.MEDIUM_STRING, nullable=False)
    last_name = orm.Column(StringTypes.MEDIUM_STRING, nullable=False)
    gender = orm.Column(orm.String(1))
    birthday = orm.Column(orm.Date)
    phone = orm.Column(StringTypes.MEDIUM_STRING)
    email = orm.Column(StringTypes.MEDIUM_STRING)
    location_id = orm.Column(orm.Integer, orm.ForeignKey('places_location.id'))

    address = orm.relationship(Location, backref='people', lazy=True)

    def __repr__(self):
        return f"<Person(id={self.id},name='{self.first_name} {self.last_name}')>"


class I18NLocaleSchema(Schema):
    id = fields.Integer(required=True, validate=Range(min=1))
    first_name = fields.String(required=True, validate=Length(min=1))
    last_name = fields.String(required=True, validate=Length(min=1))
    gender = fields.String(validate=OneOf(['M', 'F']))
    birthday = fields.Date()
    phone = fields.String()
    email = fields.String()

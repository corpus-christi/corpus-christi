import re

from flask_marshmallow import Schema
from marshmallow import fields, ValidationError, validates
from marshmallow.validate import Length

from . import orm


class StringTypes:
    SHORT_STRING = orm.String(16)
    MEDIUM_STRING = orm.String(64)
    LONG_STRING = orm.String(255)
    I18N_KEY = orm.String(32)


class I18NLocale(orm.Model):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    id = orm.Column(StringTypes.SHORT_STRING, primary_key=True)
    country = orm.Column(StringTypes.SHORT_STRING, nullable=False, default='')
    desc = orm.Column(StringTypes.MEDIUM_STRING, unique=True, nullable=False)

    def __repr__(self):
        return f"<I18NLocale(id={self.id},desc={self.desc})>"


class I18NLocaleSchema(Schema):
    id = fields.String(required=True, validate=[Length(min=2)])
    desc = fields.String(required=True, validate=[Length(min=2)])
    country = fields.String(required=True, validate=[Length(min=2)])

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]{2,}(?:-[a-z]{2,})?', id, re.IGNORECASE):
            raise ValidationError('Invalid locale code')


class I18NKey(orm.Model):
    """Key for a translatable string (e.g., 'gather.home_group')"""
    __tablename__ = 'i18n_key'
    id = orm.Column(StringTypes.I18N_KEY, primary_key=True)
    desc = orm.Column(StringTypes.LONG_STRING, unique=True, nullable=False)

    def __repr__(self):
        return "<I18NKey(key={})>".format(self.id)


class I18NKeySchema(Schema):
    id = fields.String(required=True)
    desc = fields.String(required=True)

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]+[a-z.]*[a-z]', id, re.IGNORECASE):
            raise ValidationError("Invalid id; should be of form 'abc.def.xyz'")


class I18NValue(orm.Model):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id = orm.Column(StringTypes.I18N_KEY, orm.ForeignKey('i18n_key.id'), primary_key=True)
    locale_id = orm.Column(StringTypes.SHORT_STRING, orm.ForeignKey('i18n_locale.id'), primary_key=True)
    gloss = orm.Column(orm.Text(), nullable=False)

    key = orm.relationship('I18NKey', backref='values', lazy=True)
    locale = orm.relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return "<I18NValue(gloss={})>".format(self.gloss)


class I18NValueSchema(Schema):
    key_id = fields.String(required=True)
    locale_id = fields.String(required=True)
    gloss = fields.String(required=True)

    def __repr__(self):
        return '<I18NValue(gloss={})>'.format(self.gloss)

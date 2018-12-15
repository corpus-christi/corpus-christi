import re

from flask_marshmallow import Schema
from marshmallow import fields, ValidationError, validates

from . import sqla


class StringTypes:
    SHORT_STRING = sqla.String(16)
    MEDIUM_STRING = sqla.String(64)
    LONG_STRING = sqla.String(255)
    I18N_KEY = sqla.String(32)


class I18NLocale(sqla.Model):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    id = sqla.Column(StringTypes.SHORT_STRING, primary_key=True)
    desc = sqla.Column(StringTypes.MEDIUM_STRING, unique=True, nullable=False)

    def __repr__(self):
        return f"<I18NLocale(id={self.id},desc={self.desc})>"


class I18NLocaleSchema(Schema):
    id = fields.String(required=True)
    desc = fields.String(required=True)

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]{2,}(?:-[a-z]{2,})?', id, re.IGNORECASE):
            raise ValidationError('Invalid locale code')


class I18NKey(sqla.Model):
    """Key for a translatable string (e.g., 'gather.home_group')"""
    __tablename__ = 'i18n_key'
    id = sqla.Column(StringTypes.I18N_KEY, primary_key=True)
    desc = sqla.Column(StringTypes.LONG_STRING, unique=True, nullable=False)

    def __repr__(self):
        return "<I18NKey(key={})>".format(self.id)


class I18NKeySchema(Schema):
    id = fields.String(required=True)
    desc = fields.String(required=True)

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]+[a-z.]*[a-z]', id, re.IGNORECASE):
            raise ValidationError("Invalid id; should be of form 'abc.def.xyz'")


class I18NValue(sqla.Model):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id = sqla.Column(StringTypes.I18N_KEY, sqla.ForeignKey('i18n_key.id'), primary_key=True)
    locale_id = sqla.Column(StringTypes.SHORT_STRING, sqla.ForeignKey('i18n_locale.id'), primary_key=True)
    gloss = sqla.Column(sqla.Text(), nullable=False)

    key = sqla.relationship('I18NKey', backref='values', lazy=True)
    locale = sqla.relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return "<I18NValue(gloss={})>".format(self.gloss)


class I18NValueSchema(Schema):
    key_id = fields.String(required=True)
    locale_id = fields.String(required=True)
    gloss = fields.String(required=True)

    def __repr__(self):
        return '<I18NValue(gloss={})>'.format(self.gloss)

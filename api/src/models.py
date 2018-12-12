import re

from flask_marshmallow import Schema
from marshmallow import fields, ValidationError

from . import db

StringTypes = dict(
    SHORT_STRING=db.String(16),
    MEDIUM_STRING=db.String(64),
    LONG_STRING=db.String(255),
    I18N_KEY=db.String(32)
)


class I18NLocale(db.Model):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    id = db.Column(StringTypes['SHORT_STRING'], primary_key=True)
    desc = db.Column(StringTypes['MEDIUM_STRING'], unique=True, nullable=False)

    def __repr__(self):
        return "<I18NLocale(desc={})>".format(self.desc)


def validate_i18n_locale(id):
    if not re.fullmatch(r'[a-z]{2,}(?:-[a-z]{2,})?', id, re.IGNORECASE):
        raise ValidationError('Invalid locale code')


class I18NLocaleSchema(Schema):
    id = fields.String(required=True, validate=validate_i18n_locale)
    desc = fields.String(required=True)


class I18NKey(db.Model):
    """Key for a translatable string (e.g., 'gather.home_group')"""
    __tablename__ = 'i18n_key'
    id = db.Column(StringTypes['I18N_KEY'], primary_key=True)
    desc = db.Column(StringTypes['LONG_STRING'], unique=True, nullable=False)

    def __repr__(self):
        return "<I18NKey(key={})>".format(self.id)


class I18NValue(db.Model):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id = db.Column(StringTypes['I18N_KEY'], db.ForeignKey('i18n_key.id'), primary_key=True)
    locale_id = db.Column(StringTypes['SHORT_STRING'], db.ForeignKey('i18n_locale.id'), primary_key=True)
    gloss = db.Column(db.Text(), nullable=False)

    key = db.relationship('I18NKey', backref='values', lazy=True)
    locale = db.relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return "<I18NValue(gloss={})>".format(self.gloss)

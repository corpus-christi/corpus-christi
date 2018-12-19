import re

from flask_marshmallow import Schema
from marshmallow import fields, ValidationError, validates
from marshmallow.validate import Length

from src import orm


class StringTypes:
    SHORT_STRING = orm.String(16)
    MEDIUM_STRING = orm.String(64)
    LONG_STRING = orm.String(255)
    I18N_KEY = orm.String(32)
    LOCALE_CODE = orm.String(5)


# ---- Locale

class I18NLocale(orm.Model):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    code = orm.Column(StringTypes.LOCALE_CODE, primary_key=True)
    desc = orm.Column(StringTypes.MEDIUM_STRING, unique=True, nullable=False)

    def __repr__(self):
        return f"<I18NLocale(id='{self.id}',desc='{self.desc}')>"


class I18NLocaleSchema(Schema):
    code = fields.String(required=True, validate=[Length(min=2, max=5)])
    desc = fields.String(required=True, validate=[Length(min=2)])

    @validates('code')
    def validate_id(self, code):
        if not re.fullmatch(r'[a-z]{2}-[A-Z]{2}', code, re.IGNORECASE):
            raise ValidationError('Invalid locale code')


# ---- Key

class I18NKey(orm.Model):
    """Key for a translatable string (e.g., 'groups.home_group')"""
    __tablename__ = 'i18n_key'
    id = orm.Column(StringTypes.I18N_KEY, primary_key=True)
    desc = orm.Column(StringTypes.LONG_STRING, unique=True, nullable=False)

    def __repr__(self):
        return f"<I18NKey(key='{self.id}')>"


class I18NKeySchema(Schema):
    id = fields.String(required=True)
    desc = fields.String(required=True)

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]+[a-z.]*[a-z]', id, re.IGNORECASE):
            raise ValidationError("Invalid id; should be of form 'abc.def.xyz'")


# ---- Value

class I18NValue(orm.Model):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id = orm.Column(StringTypes.I18N_KEY, orm.ForeignKey('i18n_key.id'), primary_key=True)
    locale_code = orm.Column(StringTypes.LOCALE_CODE, orm.ForeignKey('i18n_locale.code'), primary_key=True)
    gloss = orm.Column(orm.Text(), nullable=False)

    key = orm.relationship('I18NKey', backref='values', lazy=True)
    locale = orm.relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return f"<I18NValue(gloss='{self.gloss}')>"


class I18NValueSchema(Schema):
    key_id = fields.String(required=True)
    locale_code = fields.String(required=True)
    gloss = fields.String(required=True)


# ---- Language and country - https://datahub.io

class I18NLanguageCode(orm.Model):
    """ISO 639-1 language codes"""
    __tablename__ = 'i18n_language_code'
    code = orm.Column(orm.String(2), primary_key=True)
    name = orm.Column(StringTypes.SHORT_STRING, unique=True)

    def __repr__(self):
        return f"<I18NLanguageCode(code='{self.code}',name='{self.name}')>"


class I18NLanguageCodeSchema(Schema):
    code = fields.String(required=True, validate=[Length(equal=2)])
    name = fields.String(required=True, validate=[Length(min=2)])


class I18NCountryCode(orm.Model):
    """ISO 3166-1 country codes"""
    __tablename__ = 'i18n_country_code'
    code = orm.Column(orm.String(2), primary_key=True)
    name = orm.Column(StringTypes.SHORT_STRING, unique=True)

    def __repr__(self):
        return f"<I18NCountryCode(code='{self.code}',name='{self.name}')>"


class I18NCountryCodeSchema(Schema):
    code = fields.String(required=True, validate=[Length(equal=2)])
    name = fields.String(required=True, validate=[Length(min=2)])

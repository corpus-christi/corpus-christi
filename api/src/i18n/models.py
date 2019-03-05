import os
import re

from flask import json
from marshmallow import Schema
from marshmallow import fields, ValidationError, validates
from marshmallow.validate import Length
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .. import db
from ..db import Base
from ..shared.models import StringTypes


# ---- Locale

class I18NLocale(Base):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    code = Column(StringTypes.LOCALE_CODE, primary_key=True)
    desc = Column(StringTypes.MEDIUM_STRING, nullable=False)

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

class I18NKey(Base):
    """Key for a translatable string (e.g., 'groups.home_group')"""
    __tablename__ = 'i18n_key'
    id = Column(StringTypes.I18N_KEY, primary_key=True)
    desc = Column(StringTypes.LONG_STRING, nullable=False)

    def __repr__(self):
        return f"<I18NKey(key='{self.id}')>"


class I18NKeySchema(Schema):
    id = fields.String(required=True)
    desc = fields.String(required=True)

    @validates('id')
    def validate_id(self, id):
        if not re.fullmatch(r'[a-z]+[a-z.]*[a-z]', id, re.IGNORECASE):
            raise ValidationError(
                "Invalid id; should be of form 'abc.def.xyz'")


# ---- Value

class I18NValue(Base):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id = Column(StringTypes.I18N_KEY, ForeignKey(
        'i18n_key.id'), primary_key=True)
    locale_code = Column(StringTypes.LOCALE_CODE, ForeignKey(
        'i18n_locale.code'), primary_key=True)
    gloss = Column(Text(), nullable=False)

    key = relationship('I18NKey', backref='values', lazy=True)
    locale = relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return f"<I18NValue(gloss='{self.gloss}')>"


class I18NValueSchema(Schema):
    key_id = fields.String(required=True)
    locale_code = fields.String(required=True)
    gloss = fields.String(required=True)


# ---- Language

class Language(Base):
    """Language by ISO 639-1 language code"""
    __tablename__ = 'i18n_language'
    code = Column(String(2), primary_key=True)
    name_i18n = Column(StringTypes.I18N_KEY, ForeignKey(
        'i18n_key.id'), nullable=False)
    key = relationship('I18NKey', backref='languages', lazy=True)

    def __repr__(self):
        return f"<Language(code='{self.code}',name='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='language-codes.json', locale_code='en-US'):
        count = 0
        file_path = os.path.abspath(os.path.join(
            __file__, os.path.pardir, 'data', file_name))

        if not db.session.query(I18NLocale).get(locale_code):
            db.session.add(I18NLocale(code=locale_code, desc='English US'))

        with open(file_path, 'r') as fp:
            languages = json.load(fp)

            for language in languages:
                language_code = language['alpha2']
                language_name = language['English']

                name_i18n = f'language.name.{language_code}'[:32]
                i18n_create(name_i18n, locale_code,
                            language_name, description=f"Language {language_name}")

                db.session.add(cls(code=language_code, name_i18n=name_i18n))
                count += 1
            db.session.commit()
        fp.close()
        return count


# ---- CRUD


def i18n_create(key_id, locale_code, gloss, description=None):
    """Create a new value in the I18N database.

    In most cases, `description` can be omitted. It's only required
    if the I18NKey doesn't already exist.
    """
    key_id = key_id[:32]
    result = i18n_check(key_id, locale_code)
    if result is not None:
        # Already in the DB, so we can't create it.
        raise RuntimeError(f"Value {key_id}/{locale_code} already exists")

    if db.session.query(I18NLocale).get(locale_code) is None:
        # The locale isn't present; something must be horribly wrong.
        raise RuntimeError(f"No locale {locale_code}")

    try:
        # Create the key if necessary.
        key = db.session.query(I18NKey).get(key_id)
        if key is None:
            if description is None:
                raise RuntimeError(
                    f"Won't create key {key_id} without description")
            db.session.add(I18NKey(id=key_id, desc=description))

        # Add the value
        db.session.add(
            I18NValue(key_id=key_id, locale_code=locale_code, gloss=gloss))

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def i18n_read(key_id, locale_code):
    """Read an existing value from the database."""
    result = i18n_check(key_id, locale_code)
    if result is None:
        raise RuntimeError(f"No value for {key_id}/{locale_code}")
    return result


def i18n_update(key_id, locale_code, gloss):
    """Update an existing value in the I18N database."""
    result = i18n_check(key_id, locale_code)
    if result is None:
        # Not in the DB; bail.
        raise RuntimeError(f"Value {key_id}/{locale_code} doesn't exist")
    result.gloss = gloss
    db.session.commit()


def i18n_delete(key_id, locale_code):
    """Delete an existing value."""
    result = i18n_check(key_id, locale_code)
    if result is None:
        raise RuntimeError(f"Value {key_id}/{locale_code} doesn't exist")
    db.session.delete(result)
    db.session.commit()


def i18n_check(key_id, locale_code):
    """Check whether there's a value with the given key and locale."""
    return db.session.query(I18NValue).filter_by(key_id=key_id, locale_code=locale_code).first()

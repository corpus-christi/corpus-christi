import os
import re

from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base, SessionLocal
from ..shared.models import StringTypes


# ---- Locale

class I18NLocale(Base):
    """Translation locale (e.g., 'en-us', 'es')"""
    __tablename__ = 'i18n_locale'
    code: Mapped[str] = mapped_column(StringTypes.LOCALE_CODE, primary_key=True)
    desc: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)

    def __repr__(self):
        return f"<I18NLocale(code='{self.code}',desc='{self.desc}')>"


class I18NLocaleCreate(BaseModel):
    code: str
    desc: str

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not re.fullmatch(r'[a-z]{2}-[A-Z]{2}', v, re.IGNORECASE):
            raise ValueError('Invalid locale code')
        return v


class I18NLocaleRead(I18NLocaleCreate):
    model_config = ConfigDict(from_attributes=True)


# ---- Key

class I18NKey(Base):
    """Key for a translatable string (e.g., 'groups.home_group')"""
    __tablename__ = 'i18n_key'
    id: Mapped[str] = mapped_column(StringTypes.I18N_KEY, primary_key=True)
    desc: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)

    def __repr__(self):
        return f"<I18NKey(key='{self.id}')>"


class I18NKeyCreate(BaseModel):
    id: str
    desc: str

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        if not re.fullmatch(r'[a-z]+[a-z.]*[a-z]', v, re.IGNORECASE):
            raise ValueError("Invalid id; should be of form 'abc.def.xyz'")
        return v


class I18NKeyRead(I18NKeyCreate):
    model_config = ConfigDict(from_attributes=True)


# ---- Value

class I18NValue(Base):
    """Language-specific value for a given I18NKey."""
    __tablename__ = 'i18n_value'
    key_id: Mapped[str] = mapped_column(StringTypes.I18N_KEY, ForeignKey('i18n_key.id'), primary_key=True)
    locale_code: Mapped[str] = mapped_column(StringTypes.LOCALE_CODE, ForeignKey('i18n_locale.code'), primary_key=True)
    gloss: Mapped[str] = mapped_column(Text(), nullable=False)

    key = relationship('I18NKey', backref='values', lazy=True)
    locale = relationship('I18NLocale', backref='values', lazy=True)

    def __repr__(self):
        return f"<I18NValue(gloss='{self.gloss}')>"


class I18NValueCreate(BaseModel):
    key_id: str
    locale_code: str
    gloss: str


class I18NValueRead(I18NValueCreate):
    model_config = ConfigDict(from_attributes=True)


# ---- Language

class Language(Base):
    """Language by ISO 639-1 language code"""
    __tablename__ = 'i18n_language'
    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name_i18n: Mapped[str] = mapped_column(StringTypes.I18N_KEY, ForeignKey('i18n_key.id'), nullable=False)
    key = relationship('I18NKey', backref='languages', lazy=True)

    def __repr__(self):
        return f"<Language(code='{self.code}',name='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='language-codes.json', locale_code='en-US'):
        import json
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        with SessionLocal() as db:
            if not db.get(I18NLocale, locale_code):
                db.add(I18NLocale(code=locale_code, desc='English US'))

            with open(file_path, 'r') as fp:
                languages = json.load(fp)

                for language in languages:
                    language_code = language['alpha2']
                    language_name = language['English']

                    name_i18n = f'language.name.{language_code}'[:32]
                    if not i18n_check(db, name_i18n, locale_code):
                        i18n_create(db, name_i18n, locale_code,
                                    language_name, description=f"Language {language_name}")

                    if not db.get(cls, language_code):
                        db.add(cls(code=language_code, name_i18n=name_i18n))
                        count += 1
                db.commit()
        return count


# ---- CRUD


def i18n_create(db, key_id, locale_code, gloss, description=None):
    """Create a new value in the I18N database."""
    key_id = key_id[:32]
    result = i18n_check(db, key_id, locale_code)
    if result is not None:
        raise RuntimeError(f"Value {key_id}/{locale_code} already exists")

    if db.get(I18NLocale, locale_code) is None:
        raise RuntimeError(f"No locale {locale_code}")

    try:
        from sqlalchemy import select
        key = db.get(I18NKey, key_id)
        if key is None:
            if description is None:
                raise RuntimeError(f"Won't create key {key_id} without description")
            db.add(I18NKey(id=key_id, desc=description))

        db.add(I18NValue(key_id=key_id, locale_code=locale_code, gloss=gloss))
        db.commit()
    except Exception:
        db.rollback()
        raise


def i18n_read(db, key_id, locale_code):
    """Read an existing value from the database."""
    result = i18n_check(db, key_id, locale_code)
    if result is None:
        raise RuntimeError(f"No value for {key_id}/{locale_code}")
    return result


def i18n_update(db, key_id, locale_code, gloss):
    """Update an existing value in the I18N database."""
    result = i18n_check(db, key_id, locale_code)
    if result is None:
        raise RuntimeError(f"Value {key_id}/{locale_code} doesn't exist")
    result.gloss = gloss
    db.commit()


def i18n_delete(db, key_id, locale_code):
    """Delete an existing value."""
    result = i18n_check(db, key_id, locale_code)
    if result is None:
        raise RuntimeError(f"Value {key_id}/{locale_code} doesn't exist")
    db.delete(result)
    db.commit()


def i18n_check(db, key_id, locale_code):
    """Check whether there's a value with the given key and locale."""
    from sqlalchemy import select
    return db.execute(
        select(I18NValue).where(I18NValue.key_id == key_id, I18NValue.locale_code == locale_code)
    ).scalar_one_or_none()

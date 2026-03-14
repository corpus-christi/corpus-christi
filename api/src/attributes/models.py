import json
import os
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base, SessionLocal
from ..shared.models import StringTypes


# ---- Attribute

class Attribute(Base):
    __tablename__ = 'people_attributes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_i18n: Mapped[Optional[str]] = mapped_column(StringTypes.I18N_KEY)
    type_i18n: Mapped[Optional[str]] = mapped_column(StringTypes.I18N_KEY)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    enumerated_types_list = ['attribute.radio', 'attribute.check', 'attribute.dropdown']
    nonenumerated_types_list = ['attribute.float', 'attribute.integer', 'attribute.string', 'attribute.date']

    enumerated_values = relationship('EnumeratedValue', backref='attribute', lazy=True)

    def __repr__(self):
        return f"<Attribute(id={self.id})>"

    @staticmethod
    def available_types():
        return Attribute.enumerated_types_list + Attribute.nonenumerated_types_list

    @classmethod
    def load_types_from_file(cls, file_name='attribute_types.json'):
        from ..i18n.models import i18n_create, I18NLocale, i18n_check
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        with SessionLocal() as db:
            with open(file_path, 'r') as fp:
                attribute_types = json.load(fp)

                for attribute_type in attribute_types:
                    attribute_name = attribute_type['name']
                    name_i18n = f'attribute.{attribute_name}'

                    for locale in attribute_type['locales']:
                        locale_code = locale['locale_code']
                        if not db.get(I18NLocale, locale_code):
                            db.add(I18NLocale(code=locale_code, desc=''))
                        if not i18n_check(db, name_i18n, locale_code):
                            i18n_create(db, name_i18n, locale_code,
                                        locale['name'], description=f"Attribute type {attribute_name}")
                    count += 1
                db.commit()
        return count


class AttributeCreate(BaseModel):
    nameI18n: Optional[str] = None
    typeI18n: Optional[str] = None
    seq: int
    active: bool


class AttributeRead(AttributeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    enumeratedValues: List['EnumeratedValueRead'] = []


class AttributeSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        result = {
            'id': obj.id,
            'nameI18n': obj.name_i18n,
            'typeI18n': obj.type_i18n,
            'seq': obj.seq,
            'active': obj.active,
        }
        if hasattr(obj, 'enumerated_values'):
            result['enumeratedValues'] = [
                EnumeratedValueSchema()._dump_one(ev) for ev in obj.enumerated_values
            ]
        return result

    def load(self, data, partial=False):
        return {
            'name_i18n': data.get('nameI18n') or data.get('name_i18n'),
            'type_i18n': data.get('typeI18n') or data.get('type_i18n'),
            'seq': data.get('seq'),
            'active': data.get('active'),
        }


# ---- EnumeratedValue

class EnumeratedValue(Base):
    __tablename__ = 'people_enumerated_value'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('people_attributes.id'))
    value_i18n: Mapped[Optional[str]] = mapped_column(StringTypes.I18N_KEY)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self):
        return f"<EnumeratedValue(id={self.id})>"


class EnumeratedValueCreate(BaseModel):
    attributeId: Optional[int] = None
    valueI18n: Optional[str] = None
    active: bool


class EnumeratedValueRead(EnumeratedValueCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EnumeratedValueSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'attributeId': obj.attribute_id,
            'valueI18n': obj.value_i18n,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return {
            'attribute_id': data.get('attributeId') or data.get('attribute_id'),
            'value_i18n': data.get('valueI18n') or data.get('value_i18n'),
            'active': data.get('active'),
        }


# ---- Person-Attribute

class PersonAttribute(Base):
    __tablename__ = 'people_person_attributes'
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)
    attribute_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_attributes.id'), primary_key=True)
    enum_value_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('people_enumerated_value.id'), nullable=True)
    string_value: Mapped[Optional[str]] = mapped_column(StringTypes.LONG_STRING)

    person = relationship('Person', backref='person_attributes', lazy=True)
    attribute = relationship('Attribute', backref='person_attributes', lazy=True)
    enumerated_values = relationship('EnumeratedValue', backref='person_attributes', lazy=True)

    def __repr__(self):
        return f"<Person-Attribute(person_id={self.person_id},attribute_id={self.attribute_id})>"


class PersonAttributeCreate(BaseModel):
    personId: int
    attributeId: int
    enumValueId: Optional[int] = None
    stringValue: Optional[str] = None


class PersonAttributeRead(PersonAttributeCreate):
    model_config = ConfigDict(from_attributes=True)


class PersonAttributeSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'personId': obj.person_id,
            'attributeId': obj.attribute_id,
            'enumValueId': obj.enum_value_id,
            'stringValue': obj.string_value,
        }

    def load(self, data, partial=False, many=False):
        if many:
            return [self._load_one(d) for d in data]
        return self._load_one(data)

    def _load_one(self, data):
        return {
            'person_id': data.get('personId') or data.get('person_id'),
            'attribute_id': data.get('attributeId') or data.get('attribute_id'),
            'enum_value_id': data.get('enumValueId') or data.get('enum_value_id'),
            'string_value': data.get('stringValue') or data.get('string_value'),
        }

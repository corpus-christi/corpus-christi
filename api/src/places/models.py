import os
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, String, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base, SessionLocal
from ..shared.models import StringTypes


# ---- Country

class Country(Base):
    """Country; uses ISO 3166-1 country codes"""
    __tablename__ = 'places_country'
    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name_i18n: Mapped[str] = mapped_column(StringTypes.I18N_KEY, ForeignKey('i18n_key.id'), nullable=False)
    key = relationship('I18NKey', backref='countries', lazy=True)

    def __repr__(self):
        return f"<Country(code={self.code},i18n_key='{self.name_i18n}')>"

    @classmethod
    def load_from_file(cls, file_name='country-codes.json'):
        import json
        from ..i18n.models import i18n_create, I18NLocale, i18n_check
        count = 0
        file_path = os.path.abspath(os.path.join(__file__, os.path.pardir, 'data', file_name))

        with SessionLocal() as db:
            with open(file_path, 'r') as fp:
                countries = json.load(fp)

                for country in countries:
                    country_code = country['Code']
                    country_name = country['Name']
                    name_i18n = f'country.name.{country_code}'

                    for locale in country['locales']:
                        locale_code = locale['locale_code']
                        if not db.get(I18NLocale, locale_code):
                            db.add(I18NLocale(code=locale_code, desc=''))
                        if not i18n_check(db, name_i18n, locale_code):
                            i18n_create(db, name_i18n, locale_code,
                                        locale['name'], description=f"Country {country_name}")

                    from sqlalchemy import select
                    if not db.execute(select(cls).where(cls.code == country_code)).scalar_one_or_none():
                        db.add(cls(code=country_code, name_i18n=name_i18n))
                        count += 1
                db.commit()
        return count


class CountryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name_i18n: str


class CountrySchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'code': o.code, 'name_i18n': o.name_i18n} for o in obj]
        if obj is None:
            return {}
        return {'code': obj.code, 'name_i18n': obj.name_i18n}


# ---- Area

class Area(Base):
    """Generic area within country (e.g., state, province)"""
    __tablename__ = 'places_area'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), ForeignKey('places_country.code'), nullable=False)
    addresses = relationship('Address', backref='areas', passive_deletes=True)
    country = relationship('Country', backref='areas', lazy=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Area(name={self.name},Country Code='{self.country_code}')>"


class AreaCreate(BaseModel):
    name: str
    country_code: str
    active: bool = True


class AreaUpdate(BaseModel):
    name: Optional[str] = None
    country_code: Optional[str] = None
    active: Optional[bool] = None


class AreaRead(AreaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    country: Optional[CountryRead] = None


class AreaSchema:
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
            'name': obj.name,
            'country_code': obj.country_code,
            'active': obj.active,
        }


# ---- Address

class Address(Base):
    __tablename__ = 'places_address'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    address: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    city: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    area_id: Mapped[int] = mapped_column(Integer, ForeignKey('places_area.id', ondelete='CASCADE'), nullable=False)
    country_code: Mapped[str] = mapped_column(StringTypes.SHORT_STRING, ForeignKey('places_country.code'), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    country = relationship('Country', backref='addresses', lazy=True)
    meetings = relationship('Meeting', back_populates='address', lazy=True)
    locations = relationship('Location', back_populates='address', lazy=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Address(id={self.id},name={self.name})>"


class AddressCreate(BaseModel):
    name: str
    address: str
    city: str
    area_id: int
    country_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active: bool = True


class AddressUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    area_id: Optional[int] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active: Optional[bool] = None


class AddressRead(AddressCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    area: Optional[AreaRead] = None
    country: Optional[CountryRead] = None


class AddressSchema:
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
            'name': obj.name,
            'address': obj.address,
            'city': obj.city,
            'area_id': obj.area_id,
            'country_code': obj.country_code,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return data


# ---- Location

class Location(Base):
    __tablename__ = 'places_location'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(StringTypes.MEDIUM_STRING)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey('places_address.id'), nullable=False)
    address = relationship('Address', back_populates='locations', lazy=True)
    events = relationship('Event', back_populates="location")
    assets = relationship('Asset', back_populates="location")
    images = relationship('ImageLocation', back_populates="location")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Location(id={self.id})>"


class LocationCreate(BaseModel):
    description: Optional[str] = None
    address_id: int
    active: bool = True


class LocationUpdate(BaseModel):
    description: Optional[str] = None
    address_id: Optional[int] = None
    active: Optional[bool] = None


class LocationRead(LocationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    address: Optional[AddressRead] = None


class LocationSchema:
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
            'description': obj.description,
            'address_id': obj.address_id,
            'active': obj.active,
        }

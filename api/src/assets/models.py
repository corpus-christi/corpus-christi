from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Asset

class Asset(Base):
    __tablename__ = 'events_asset'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('places_location.id'))
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    events = relationship("EventAsset", back_populates="asset")
    location = relationship("Location", back_populates="assets")

    def __repr__(self):
        return f"<Asset(id={self.id})>"


class AssetCreate(BaseModel):
    description: str
    location_id: Optional[int] = None
    active: Optional[bool] = True


class AssetUpdate(BaseModel):
    description: Optional[str] = None
    location_id: Optional[int] = None
    active: Optional[bool] = None


class AssetRead(AssetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_count: Optional[int] = None


class AssetSchema:
    """Compat shim."""
    def __init__(self, exclude=None):
        self.exclude = exclude or []

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
            'location_id': obj.location_id,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return data

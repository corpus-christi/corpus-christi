from marshmallow import fields, Schema
from marshmallow.validate import Range
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from ..db import Base
from ..shared.models import StringTypes


# ---- Asset

class Asset(Base):
    __tablename__ = 'events_asset'
    id = Column(Integer, primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    location_id = Column(Integer, ForeignKey('places_location.id'))
    active = Column(Boolean, default=True)

    events = relationship("EventAsset", back_populates="asset")
    location = relationship("Location", back_populates="assets")
    collections = relationship("AssetCollection", back_populates="asset")

    def __repr__(self):
        return f"<Asset(id={self.id})>"


class AssetSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    description = fields.String(required=True)
    location = fields.Nested('LocationSchema', dump_only=True)
    location_id = fields.Integer(required=True, min=1)
    active = fields.Boolean(default=True)
    event_count = fields.Integer(dump_only=True)

# ---- Collection

class Collection(Base):
    __tablename__ = 'events_collection'
    id = Column(Integer, primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)

    assets = relationship("AssetCollection", back_populates="collection")

class CollectionSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    description = fields.String(required=True)

    assets = fields.Nested('AssetCollectionSchema', dump_only=True)

# ---- AssetCollection

class AssetCollection(Base):
    __tablename__ = 'events_assetcollection'
    asset_id = Column(Integer, ForeignKey('events_asset.id'), primary_key=True)
    collection_id = Column(Integer, ForeignKey('events_collection.id'), primary_key=True)

    asset = relationship("Asset", back_populates="collections")
    collection = relationship("Collection", back_populates="assets")

class AssetCollectionSchema(Schema):
    asset_id = fields.Integer(required=True, min=1)
    collection_id = fields.Integer(required=True, min=1)

    asset = fields.Nested('AssetSchema', dump_only=True)
    collection = fields.Nested('CollectionSchema', dump_only=True)

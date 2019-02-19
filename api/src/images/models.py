from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..shared.models import StringTypes
from ..people.models import Person

# ---- Image


class Image(Base):
    __tablename__ = 'images_image'
    id = Column(Integer, primary_key=True)
    path = Column(StringTypes.LONG_STRING, unique=False, nullable=False)
    description = Column(StringTypes.LONG_STRING, default=None)

    events = relationship("ImageEvent", back_populates="image")


class ImageSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, min=1)
    path = fields.String(required=True)
    description = fields.String(allow_none=True)

    events = fields.Nested('EventSchema', dump_only=True)


class ImageEvent(Base):
    __tablename__ = 'images_imageevent'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events_event.id"), primary_key=True)

    image = relationship("Image", back_populates="events")
    event = relationship("Event", back_populates="images")


class ImageEventSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    event_id = fields.Integer(required=True, min=1)

    event = fields.Nested('EventSchema', dump_only=True)
    image = fields.Nested('ImageSchema', exclude=['events'], dump_only=True)

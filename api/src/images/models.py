from marshmallow import fields, Schema
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..db import Base
from ..shared.models import StringTypes


# ---- Image


class Image(Base):
    __tablename__ = 'images_image'
    id = Column(Integer, primary_key=True)
    path = Column(StringTypes.LONG_STRING, unique=False, nullable=False)
    description = Column(StringTypes.LONG_STRING, default=None)

    events = relationship("ImageEvent", backref="image")
    people = relationship("ImagePerson", backref="image")
    courses = relationship("ImageCourse", backref="image")
    groups = relationship("ImageGroup", backref="image")
    locations = relationship("ImageLocation", backref="image")


class ImageSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, min=1)
    path = fields.String(required=True)
    description = fields.String(allow_none=True)

    events = fields.Nested('EventSchema', dump_only=True)


class ImageEvent(Base):
    __tablename__ = 'images_imageevent'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events_event.id"), primary_key=True)

    image = relationship("Image", backref="events")
    event = relationship("Event", backref="images")


class ImageEventSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    event_id = fields.Integer(required=True, min=1)

    image = fields.Nested('ImageSchema', dump_only=True)
    event = fields.Nested('EventSchema', dump_only=True)


class ImagePerson(Base):
    __tablename__ = 'images_imageperson'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    person_id = Column(Integer, ForeignKey(
        "people_person.id"), primary_key=True)

    image = relationship("Image", backref="people")
    person = relationship("Person", backref="images")


class ImagePersonSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    person_id = fields.Integer(required=True, min=1)

    image = fields.Nested('ImageSchema', dump_only=True)
    person = fields.Nested('PersonSchema', dump_only=True)


class ImageCourse(Base):
    __tablename__ = 'images_imagecourse'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey(
        "courses_course.id"), primary_key=True)

    image = relationship("Image", backref="courses")
    course = relationship("Course", backref="images")


class ImageCourseSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    course_id = fields.Integer(required=True, min=1)

    image = fields.Nested('ImageSchema', dump_only=True)
    course = fields.Nested('CourseSchema', dump_only=True)


class ImageGroup(Base):
    __tablename__ = 'images_imagegroup'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups_group.id"), primary_key=True)

    image = relationship("Image", backref="groups")
    group = relationship("Group", backref="images")


class ImageGroupSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    group_id = fields.Integer(required=True, min=1)

    image = fields.Nested('ImageSchema', dump_only=True)
    group = fields.Nested('GroupSchema', dump_only=True)


class ImageLocation(Base):
    __tablename__ = 'images_imagelocation'
    image_id = Column(Integer, ForeignKey("images_image.id"), primary_key=True)
    location_id = Column(Integer, ForeignKey(
        "places_location.id"), primary_key=True)

    image = relationship("Image", backref="locations")
    location = relationship("Location", backref="images")


class ImageLocationSchema(Schema):
    image_id = fields.Integer(required=True, min=1)
    location_id = fields.Integer(required=True, min=1)

    image = fields.Nested('ImageSchema', dump_only=True)
    location = fields.Nested('LocationSchema', dump_only=True)

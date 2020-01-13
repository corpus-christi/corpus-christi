from marshmallow import fields, Schema
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..db import Base
from ..shared.models import StringTypes


# ---- Image


class Image(Base):
    __tablename__ = 'images_image'
    id = Column(Integer, primary_key=True)
    path = Column(StringTypes.LONG_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    groups = relationship('ImageGroup', backref='images', lazy=True)
    courses = relationship('ImageCourse', backref='images', lazy=True)
    locations = relationship('ImageLocation', backref='images', lazy=True)
    people = relationship('ImagePerson', backref='images', lazy=True)
    events = relationship('ImageEvents', backref='images', lazy=True)

    def __repr__(self):
        return f"<Image(id={self.id})>"


class ImageSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    path = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))

    events = fields.Nested('EventSchema', dump_only=True)


# ---- ImageGroup


class ImageGroup(Base):
    __tablename__ = 'images_imagegroup'
    image_id = Column(Integer, ForeignKey(
        'images_image.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey(
        'groups_group.id'), primary_key=True)

    def __repr__(self):
        return f"<ImageGroup(image_id={self.image_id},group_id={self.group_id})>"


class ImageGroupSchema(Schema):
    image_id = fields.Integer(
        dump_only=True, data_key='imageId', required=True)
    group_id = fields.Integer(
        dump_only=True, data_key='groupId', required=True)

    # TODO: if commenting these out doesn't break anything delete them
    # image = fields.Nested('ImageSchema', dump_only=True)
    # group = fields.Nested('GroupSchema', dump_only=True)


# ---- ImageCourse


class ImageCourse(Base):
    __tablename__ = 'images_imagecourse'
    image_id = Column(Integer, ForeignKey(
        'images_image.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)

    def __repr__(self):
        return f"<ImageCourse(image_id={self.image_id},course_id={self.course_id})>"


class ImageCourseSchema(Schema):
    image_id = fields.Integer(
        dump_only=True, data_key='imageId', required=True)
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)

    # TODO: if commenting these out doesn't break anything delete them
    # image = fields.Nested('ImageSchema', dump_only=True)
    # course = fields.Nested('CourseSchema', dump_only=True)


# ---- ImageLocation


class ImageLocation(Base):
    __tablename__ = 'images_imagelocation'
    image_id = Column(Integer, ForeignKey(
        'images_image.id'), primary_key=True)
    location_id = Column(Integer, ForeignKey(
        'places_location.id'), primary_key=True)

    def __repr__(self):
        return f"<ImageLocation(image_id={self.image_id},location_id={self.location_id})>"


class ImageLocationSchema(Schema):
    image_id = fields.Integer(
        dump_only=True, data_key='imageId', required=True)
    location_id = fields.Integer(
        dump_only=True, data_key='locationId', required=True)

    # TODO: if commenting these out doesn't break anything delete them
    # image = fields.Nested('ImageSchema', dump_only=True)
    # location = fields.Nested('LocationSchema', dump_only=True)


# ---- ImagePerson


class ImagePerson(Base):
    __tablename__ = 'images_imageperson'
    image_id = Column(Integer, ForeignKey(
        'images_image.id'), primary_key=True)
    location_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)

    def __repr__(self):
        return f"<ImagePerson(image_id={self.image_id},location_id={self.location_id})>"


class ImagePersonSchema(Schema):
    image_id = fields.Integer(
        dump_only=True, data_key='imageId', required=True)
    location_id = fields.Integer(
        dump_only=True, data_key='locationId', required=True)

    # TODO: if commenting these out doesn't break anything delete them
    # image = fields.Nested('ImageSchema', dump_only=True)
    # person = fields.Nested('PersonSchema', dump_only=True)


# ---- ImageEvent


class ImageEvent(Base):
    __tablename__ = 'images_imageevent'
    image_id = Column(Integer, ForeignKey(
        'images_image.id'), primary_key=True)
    event_id = Column(Integer, ForeignKey(
        'events_event.id'), primary_key=True)

    def __repr__(self):
        return f"<ImageEvent(image_id={self.image_id},event_id={self.event_id})>"


class ImageEventSchema(Schema):
    image_id = fields.Integer(
        dump_only=True, data_key='imageId', required=True)
    event_id = fields.Integer(
        dump_only=True, data_key='eventId', required=True)

    # TODO: if commenting these out doesn't break anything delete them
    # image = fields.Nested('ImageSchema', dump_only=True)
    # event = fields.Nested('EventSchema', dump_only=True)

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Image

class Image(Base):
    __tablename__ = 'images_image'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(StringTypes.LONG_STRING, unique=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(StringTypes.LONG_STRING, default=None)

    events = relationship("ImageEvent", back_populates="image")
    people = relationship("ImagePerson", back_populates="image")
    courses = relationship("ImageCourse", back_populates="image")
    groups = relationship("ImageGroup", back_populates="image")
    locations = relationship("ImageLocation", back_populates="image")


class ImageCreate(BaseModel):
    path: str
    description: Optional[str] = None


class ImageRead(ImageCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ImageSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {'id': obj.id, 'path': obj.path, 'description': obj.description}

    def load(self, data, partial=False):
        return data


class ImageEvent(Base):
    __tablename__ = 'images_imageevent'
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images_image.id"), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events_event.id"), primary_key=True)

    image = relationship("Image", back_populates="events")
    event = relationship("Event", back_populates="images")


class ImageEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    image_id: int
    event_id: int


class ImageEventSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'image_id': o.image_id, 'event_id': o.event_id} for o in obj]
        if obj is None:
            return {}
        return {'image_id': obj.image_id, 'event_id': obj.event_id}


class ImagePerson(Base):
    __tablename__ = 'images_imageperson'
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images_image.id"), primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("people_person.id"), primary_key=True)

    image = relationship("Image", back_populates="people")
    person = relationship("Person", back_populates="images")


class ImagePersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    image_id: int
    person_id: int


class ImagePersonSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'image_id': o.image_id, 'person_id': o.person_id} for o in obj]
        if obj is None:
            return {}
        return {'image_id': obj.image_id, 'person_id': obj.person_id}


class ImageCourse(Base):
    __tablename__ = 'images_imagecourse'
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images_image.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses_course.id"), primary_key=True)

    image = relationship("Image", back_populates="courses")
    course = relationship("Course", back_populates="images")


class ImageCourseSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'image_id': o.image_id, 'course_id': o.course_id} for o in obj]
        if obj is None:
            return {}
        return {'image_id': obj.image_id, 'course_id': obj.course_id}


class ImageGroup(Base):
    __tablename__ = 'images_imagegroup'
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images_image.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups_group.id"), primary_key=True)

    image = relationship("Image", back_populates="groups")
    group = relationship("Group", back_populates="images")


class ImageGroupSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'image_id': o.image_id, 'group_id': o.group_id} for o in obj]
        if obj is None:
            return {}
        return {'image_id': obj.image_id, 'group_id': obj.group_id}


class ImageLocation(Base):
    __tablename__ = 'images_imagelocation'
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images_image.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("places_location.id"), primary_key=True)

    image = relationship("Image", back_populates="locations")
    location = relationship("Location", back_populates="images")


class ImageLocationSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [{'image_id': o.image_id, 'location_id': o.location_id} for o in obj]
        if obj is None:
            return {}
        return {'image_id': obj.image_id, 'location_id': obj.location_id}

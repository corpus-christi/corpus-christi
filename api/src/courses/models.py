from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from src.shared.models import StringTypes

# ---- Course

class Course(Base):
     __tablename__ = 'courses_course'
     id = Column(Integer, primary_key=True)
     name = Column(StringTypes.MEDIUM_STRING, nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     active = Column(Boolean, nullable=False, default=True)

     def __repr__(self):
         return f"<Course(id={self.id})>"


class CourseSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     name = fields.String(required=True, validate=Length(min=1))
     description = fields.String(required=True, validate=Length(min=1))
     active = fields.Boolean(required=True)

# ---- Prerequisite

class Prerequisite(Base):
     __tablename__ = 'courses_offering'
     id = Column(Integer, primary_key=True)
     course_id = Column(Integer, ForeignKey('courses_course.id'), nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     max_size = Column(Integer, nullable=False)
     active = Column(Boolean, nullable=False, default=True)

     def __repr__(self):
         return f"<Prerequisite(id={self.id})>"


class PrerequisiteSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     course_id = fields.Integer(data_key='courseId', required=True)
     description = fields.String(required=True, validate=Length(min=1))
     max_size = fields.Integer(data_key='maxSize', required=True)
     active = fields.Boolean(required=True)

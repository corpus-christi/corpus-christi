#Completed by Ryan and Eliza 01/08/2019 2:45pm
from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from src.db import Base
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
     __tablename__ = 'courses_prerequisite'
     course_id = Column(Integer, ForeignKey('courses_course.id'), primary_key=True)
     prereq_id = Column(Integer, ForeignKey('courses_course.id'), primary_key=True)

     def __repr__(self):
          return f"<Prerequisite(course_id={self.course_id},prereq_id={self.prereq_id})>"
    

class PrerequisiteSchema(Schema):
     course_id = fields.Integer(dump_only=True, data_key='courseId', required=True)
     prereq_id = fields.Integer(dump_only=True, data_key='prereqId', required=True)

# ---- Course_Offering

class Course_Offering(Base):
     __tablename__ = 'courses_offering'
     id = Column(Integer, primary_key=True)
     course_id = Column(Integer, ForeignKey('courses_course.id'), nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     max_size = Column(Integer, nullable=False)
     active = Column(Boolean, nullable=False, default=True)

     def __repr__(self):
          return f"<Course_Offering(id={self.id})>"
    

class Course_OfferingSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     course_id = fields.Integer(data_key='courseId', required=True)
     description = fields.String(required=True, validate=Length(min=1))
     max_size = fields.Integer(data_key='maxSize', required=True)
     active = fields.Boolean(required=True)
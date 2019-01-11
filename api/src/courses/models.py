#Completed by Ryan and Eliza 01/08/2019 2:45pm
from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime, Table
from sqlalchemy.orm import relationship

from src.db import Base
from src.shared.models import StringTypes

# ---- Prerequisite

Prerequisite = Table('courses_prerequisite', Base.metadata,
        Column('course_id', Integer, ForeignKey('courses_course.id'), primary_key=True),
        Column('prereq_id', Integer, ForeignKey('courses_course.id'), primary_key=True))


class PrerequisiteSchema(Schema):
     course_id = fields.Integer(data_key='courseId', required=True)
     prereq_id = fields.Integer(data_key='prereqId', required=True)

# ---- Diploma_Course

Diploma_Course = Table('courses_diploma_course', Base.metadata,
          Column('course_id', Integer, ForeignKey('courses_course.id'), primary_key=True),
          Column('diploma_id', Integer, ForeignKey('courses_diploma.id'), primary_key=True))

class Diploma_CourseSchema(Schema):
     course_id = fields.Integer(dump_only=True, data_key='courseId', required=True)
     diploma_id = fields.Integer(dump_only=True, data_key='diplomaId', required=True)

# ---- Course

class Course(Base):
     __tablename__ = 'courses_course'
     id = Column(Integer, primary_key=True)
     name = Column(StringTypes.MEDIUM_STRING, nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     active = Column(Boolean, nullable=False, default=True)
     depend = relationship('Course', secondary=Prerequisite,
                primaryjoin=Prerequisite.c.course_id==id,
                secondaryjoin=Prerequisite.c.prereq_id==id,
                foreign_keys=[Prerequisite.c.course_id, Prerequisite.c.prereq_id],
                backref='prerequisites',  lazy=True)
     prerequisite = relationship('Course', secondary=Prerequisite,
                primaryjoin=Prerequisite.c.prereq_id==id,
                secondaryjoin=Prerequisite.c.course_id==id,
                foreign_keys=[Prerequisite.c.course_id, Prerequisite.c.prereq_id],
                backref='depends', lazy=True)
     diploma = relationship('Diploma', secondary=Diploma_Course, backref='courses', lazy=True)

     def __repr__(self):
         return f"<Course(id={self.id})>"


class CourseSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     name = fields.String(required=True, validate=Length(min=1))
     description = fields.String(required=True, validate=Length(min=1))
     active = fields.Boolean(required=True)

# ---- Diploma_Awarded

Diploma_Awarded = Table('courses_diploma_awarded', Base.metadata,
          Column('student_id', Integer, ForeignKey('courses_students.id'), primary_key=True),
          Column('diploma_id', Integer, ForeignKey('courses_diploma.id'), primary_key=True),
          Column('when', Date, nullable=False))


class Diploma_AwardedSchema(Schema):
     student_id = fields.Integer(dump_only=True, data_key='studentId', required=True, validate=Range(min=1))
     diploma_id = fields.Integer(dump_only=True, data_key='diplomaId', required=True, validate=Range(min=1))
     when = fields.Date(required=True)

# ---- Diploma

class Diploma(Base):
     __tablename__ = 'courses_diploma'
     id = Column(Integer, primary_key=True)
     name = Column(StringTypes.MEDIUM_STRING, nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     active = Column(Boolean, nullable=False, default=True)
     course = relationship('Course', secondary=Diploma_Course,
               backref='diplomas', lazy=True)
     student = relationship('Student', secondary=Diploma_Awarded,
               backref='students', lazy=True)


     def __repr__(self):
         return f"<Diploma(id={self.id})>"


class DiplomaSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     name = fields.String(required=True, validate=Length(min=1))
     description = fields.String(required=True, validate=Length(min=1))
     active = fields.Boolean(required=True)

# ---- Student

class Student(Base):
     __tablename__ = 'courses_students'
     id = Column(Integer, primary_key=True)
     offering_id = Column(Integer, ForeignKey('courses_course_offering.id'), nullable=False)
     student_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)
     confirmed = Column(Boolean, nullable=False)
     course_offering = relationship('Course_Offering', backref='offerings', lazy=True)
     person = relationship('Person', backref='students', lazy=True)
     diploma = relationship('Student', secondary=Diploma_Awarded,
     backref='diplomas', lazy=True)


     def __repr__(self):
         return f"<Student(id={self.id})>"


class StudentSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     offering_id = fields.Integer(data_key='offeringId', required=True)
     student_id = fields.Integer(data_key='studentId', required=True)
     confirmed = fields.Boolean(required=True)

# ---- Course_Offering

class Course_Offering(Base):
     __tablename__ = 'courses_course_offering'
     id = Column(Integer, primary_key=True)
     course_id = Column(Integer, ForeignKey('courses_course.id'), nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     max_size = Column(Integer, nullable=False)
     active = Column(Boolean, nullable=False, default=True)
     course = relationship('Course', backref='courses_offered', lazy=True)

     def __repr__(self):
         return f"<Course_Offering(id={self.id})>"

class Course_OfferingSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     course_id = fields.Integer(data_key='courseId', required=True)
     description = fields.String(required=True, validate=Length(min=1))
     max_size = fields.Integer(data_key='maxSize', required=True)
     active = fields.Boolean(required=True)

# ---- Class_Meeting

# class Class_Meeting(Base):
#      __tablename__ = 'courses_class_meeting'
#      id = Column(Integer, primary_key=True)
#      offering_id = Column(Integer, ForeignKey('courses_course_offering.id'), nullable=False)
#      location = Column(Integer, ForeignKey('places_location.id'), nullable=False)
#      teacher = Column(Integer, ForeignKey('people_person.id'), nullable=False)
#      when = Column(DateTime, nullable=False)
#      course_offering = relationship('Course_Offering', backref='class_meeting', lazy=True)
#      location = relationship('Location', backref='meeting_location', lazy=True)
#      person = relationship('Person', backref='teacher', lazy=True)
#
#      def __repr__(self):
#          return f"<Class_Meeting(id={self.id})>"


# class Class_MeetingSchema(Schema):
#     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
#     offering_id = fields.Integer(data_key='offeringId', required=True)
#     location = fields.Integer(required=True)
#     teacher = fields.Integer(required=True)
#     when = fields.DateTime(required=True)

# ---- Class_Attendance

# class Class_Attendance(Base):
#     __tablename__ = 'courses_class_attendance'
#     class_id = Column(Integer, ForeignKey('courses_class_meeting.id'), primary_key=True)
#     student_id = Column(Integer, ForeignKey('courses_students.id'), primary_key=True)
#     lecture = relationship('Class_Meeting', backref='attendance', foreign_keys=[class_id], lazy=True)
#     students = relationship('Student', backref='students', foreign_keys=[student_id], lazy=True)
#
#     def __repr__(self):
#         return f"<Class_Attendance(class_id={self.class_id},student_id={self.student_id})>"
#
#
# class Class_AttendanceSchema(Schema):
#     class_id = fields.Integer(dump_only=True, data_key='classId', required=True)
#     student_id = fields.Integer(dump_only=True, data_key='studentId', required=True)

from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime, Table
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
    images = relationship('ImageCourse', backref='courses', lazy=True)

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
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)
    prereq_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)
    courses = relationship('Course', backref='prerequisites', lazy=True)
    prereqs = relationship('Course', backref='prerequisites', lazy=True)

    def __repr__(self):
            return f"<Prerequisite(course_id={self.course_id},prereq_id={self.prereq_id})>"


class PrerequisiteSchema(Schema):
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)
    prereq_id = fields.Integer(
        dump_only=True, data_key='prereqId', required=True)

# ---- DiplomaCourse


class DiplomaCourse(Base):
    __tablename__ = 'courses_diploma_course'
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)
    diploma_id = Column(Integer, ForeignKey(
        'courses_diploma.id'), primary_key=True)

    def __repr__(self):
            return f"<DiplomaCourse(course_id={self.course_id},diploma_id={self.diploma_id})>"


class DiplomaCourseSchema(Schema):
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)
    diploma_id = fields.Integer(
        dump_only=True, data_key='diplomaId', required=True)

# ---- Diploma


class Diploma(Base):
    __tablename__ = 'courses_diploma'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
            return f"<Diploma(id={self.id})>"


class DiplomaSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    active = fields.Boolean(required=True)


# ---- DiplomaAwarded


class DiplomaAwarded(Base):
    __tablename__ = 'courses_diploma_awarded'
    student_id = Column(Integer, ForeignKey(
        'courses_student.id'), primary_key=True)
    diploma_id = Column(Integer, ForeignKey(
        'courses_diploma.id'), primary_key=True)
    when = Column(Date, nullable=False)

    def __repr__(self):
            return f"<DiplomaAwarded(student_id={self.student_id},diploma_id={self.diploma_id})>"


class DiplomaAwardedSchema(Schema):
    student_id = fields.Integer(
        dump_only=True, data_key='studentId', required=True, validate=Range(min=1))
    diploma_id = fields.Integer(
        dump_only=True, data_key='diplomaId', required=True, validate=Range(min=1))
    when = fields.Date(required=True)







# ---- Student


class Student(Base):
    __tablename__ = 'courses_students'
    id = Column(Integer, primary_key=True)
    offering_id = Column(Integer, ForeignKey(
        'courses_course_offering.id'), nullable=False)
    student_id = Column(Integer, ForeignKey(
        'people_person.id'), nullable=False)
    confirmed = Column(Boolean, nullable=False)
    course_offerings = relationship(
        'Course_Offering', backref='offerings', lazy=True)
    people = relationship('Person', backref='students', lazy=True)

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
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    max_size = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    courses = relationship('Course', backref='courses_offered', lazy=True)

    def __repr__(self):
            return f"<Course_Offering(id={self.id})>"


class Course_OfferingSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    course_id = fields.Integer(data_key='courseId', required=True)
    description = fields.String(required=True, validate=Length(min=1))
    max_size = fields.Integer(data_key='maxSize', required=True)
    active = fields.Boolean(required=True)

# ---- Class_Attendance


class Class_Attendance(Base):
    __tablename__ = 'courses_class_attendance'
    class_id = Column(Integer, ForeignKey(
        'courses_class_meeting.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey(
        'courses_student.id'), primary_key=True)

    def __repr__(self):
            return f"<Class_Attendance(class_id={self.class_id},student_id={self.student_id})>"


class Class_AttendanceSchema(Schema):
    class_id = fields.Integer(
        dump_only=True, data_key='classId', required=True)
    student_id = fields.Integer(
        dump_only=True, data_key='studentId', required=True)


# ---- ClassMeeting


class ClassMeeting(Base):
    __tablename__ = 'courses_class_meeting'
    id = Column(Integer, primary_key=True)
    offering_id = Column(Integer, ForeignKey(
        'courses_course_offering.id'), nullable=False)
    location = Column(Integer, ForeignKey(
        'places_location.id'), nullable=False)
    teacher = Column(Integer, ForeignKey('people_person.id'), nullable=False)
    when = Column(Datetime, nullable=False)
    course_offerings = relationship(
        'Course_Offering', backref='class_meeting', lazy=True)
    locations = relationship('Location', backref='meeting_location', lazy=True)
    people = relationship('Person', backref='teacher', lazy=True)

    def __repr__(self):
            return f"<ClassMeeting(id={self.id})>"


class ClassMeetingSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    offering_id = fields.Integer(data_key='offeringId', required=True)
    location = fields.Integer(required=True)
    teacher = fields.Integer(required=True)
    when = fields.DateTime(required=True)

# ---- CourseCompletion


class CourseCompletion(Base):
    __tablename__ = 'courses_course_completion'
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)

    def __repr__(self):
        return f"<CourseCompletion(course_id={self.course_id},person_id={self.person_id})>"


class CourseCompletionSchema(Schema):
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)
    person_id = fields.Integer(
        dump_only=True, data_key='personId', required=True)

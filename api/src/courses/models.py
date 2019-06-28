from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime, Table
from sqlalchemy.orm import relationship
from src.db import Base
from src.shared.models import StringTypes


# ---- Prerequisite

Prerequisite = Table('courses_prerequisite', Base.metadata,
                     Column('course_id', Integer, ForeignKey(
                         'courses_course.id'), primary_key=True),
                     Column('prereq_id', Integer, ForeignKey('courses_course.id'), primary_key=True))


class PrerequisiteSchema(Schema):
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)
    prereq_id = fields.Integer(
        dump_only=True, data_key='prereqId', required=True)

# ---- DiplomaCourse


DiplomaCourse = Table('courses_diploma_course', Base.metadata,
                      Column('course_id', Integer, ForeignKey(
                           'courses_course.id'), primary_key=True),
                      Column('diploma_id', Integer, ForeignKey('courses_diploma.id'), primary_key=True))


class DiplomaCourseSchema(Schema):
    course_id = fields.Integer(
        dump_only=True, data_key='courseId', required=True)
    diploma_id = fields.Integer(
        dump_only=True, data_key='diplomaId', required=True)

# ---- DiplomaAwarded


class DiplomaAwarded(Base):
    __tablename__ = 'courses_diploma_awarded'
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)
    diploma_id = Column(Integer, ForeignKey(
        'courses_diploma.id'), primary_key=True)
    when = Column(Date, nullable=True)

    students = relationship(
        'Person', back_populates='diplomas_awarded', lazy=True)
    diplomas = relationship(
        'Diploma', back_populates='diplomas_awarded', lazy=True)

    def __repr__(self):
        return f"<DiplomaAwarded(student_id={self.person_id},diploma_id={self.diploma_id})>"


class DiplomaAwardedSchema(Schema):
    person_id = fields.Integer(
        data_key='personId', required=True, validate=Range(min=1))
    diploma_id = fields.Integer(
        data_key='diplomaId', required=True, validate=Range(min=1))
    when = fields.Date(required=True, allow_none=True)

# ---- Class_Attendance


ClassAttendance = Table('courses_class_attendance', Base.metadata,
                        Column('class_id', Integer, ForeignKey(
                            'courses_class_meeting.id'), primary_key=True),
                        Column('student_id', Integer, ForeignKey('courses_students.id'), primary_key=True))


class ClassAttendanceSchema(Schema):
    class_id = fields.Integer(
        dump_only=True, data_key='classId', required=True)
    student_id = fields.Integer(
        dump_only=True, data_key='studentId', required=True)

# --- Course_Completion


class CourseCompletion(Base):
    __tablename__ = 'courses_course_completion'
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)

    people = relationship('Person', backref='completions', lazy=True)
    courses = relationship('Course', backref='completions', lazy=True)

    def __repr__(self):
        return f"<Course_Completion(course_id={self.course_id},person_id={self.person_id})>"


class CourseCompletionSchema(Schema):
    course_id = fields.Integer(data_key='courseId', required=True)
    person_id = fields.Integer(data_key='personId', required=True)

# ---- Course


class Course(Base):
    __tablename__ = 'courses_course'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    depends = relationship('Course', secondary=Prerequisite,
                           foreign_keys=[Prerequisite.c.course_id,
                                         Prerequisite.c.prereq_id],
                           primaryjoin=Prerequisite.c.prereq_id == id,
                           secondaryjoin=Prerequisite.c.course_id == id,
                           back_populates='prerequisites',  lazy=True)
    prerequisites = relationship('Course', secondary=Prerequisite,
                                 primaryjoin=Prerequisite.c.course_id == id,
                                 secondaryjoin=Prerequisite.c.prereq_id == id,
                                 foreign_keys=[
                                     Prerequisite.c.course_id, Prerequisite.c.prereq_id],
                                 back_populates='depends', lazy=True)
    diplomas = relationship(
        'Diploma', secondary=DiplomaCourse, back_populates='courses', lazy=True)
    images = relationship("ImageCourse", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id})>"


class CourseSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    active = fields.Boolean(required=True, default=True)
    diplomaList = fields.Nested('DiplomaSchema', many=True)
    images = fields.Nested('ImageCourseSchema', many=True,
                           exclude=['course'], dump_only=True)

# ---- Diploma


class Diploma(Base):
    __tablename__ = 'courses_diploma'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    courses = relationship('Course', secondary=DiplomaCourse,
                           back_populates='diplomas', lazy=True)
    diplomas_awarded = relationship('DiplomaAwarded',
                                    back_populates='diplomas', lazy=True)

    def __repr__(self):
        return f"<Diploma(id={self.id})>"


class DiplomaSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(allow_none=True)
    active = fields.Boolean(required=False, default=True)
    courseList = fields.Nested('CourseSchema', many=True)
    studentList = fields.Nested('StudentSchema', many=True)

# ---- Student


class Student(Base):
    __tablename__ = 'courses_students'
    id = Column(Integer, primary_key=True)
    offering_id = Column(Integer, ForeignKey(
        'courses_course_offering.id'), nullable=False)
    student_id = Column(Integer, ForeignKey(
        'people_person.id'), nullable=False)
    confirmed = Column(Boolean, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    courses_offered = relationship(
        'Course_Offering', back_populates='students', lazy=True)
    person = relationship('Person', backref='students', lazy=True)
    attendance = relationship('ClassMeeting', secondary=ClassAttendance,
                              back_populates='students', lazy=True)

    def __repr__(self):
        return f"<Student(id={self.id})>"


class StudentSchema(Schema):
    id = fields.Integer(validate=Range(min=1))
    offering_id = fields.Integer(data_key='offeringId', required=True)
    student_id = fields.Integer(data_key='studentId', required=True)
    confirmed = fields.Boolean(required=True, default=False)
    active = fields.Boolean(required=True, default=True)
    diplomaList = fields.Nested('DiplomaSchema', many=True)

# ---- Course_Offering


class Course_Offering(Base):
    __tablename__ = 'courses_course_offering'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey(
        'courses_course.id'), nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    max_size = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    students = relationship(
        'Student', back_populates='courses_offered', lazy=True)
    course = relationship('Course', backref='courses_offered', lazy=True)

    def __repr__(self):
        return f"<Course_Offering(id={self.id})>"


class CourseOfferingSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    course_id = fields.Integer(data_key='courseId', required=False)
    description = fields.String(required=True, validate=Length(min=1))
    max_size = fields.Integer(
        data_key='maxSize', required=True, validate=Range(min=1))
    active = fields.Boolean(required=False, default=True)

# ---- ClassMeeting


class ClassMeeting(Base):
    __tablename__ = 'courses_class_meeting'
    id = Column(Integer, primary_key=True)
    offering_id = Column(Integer, ForeignKey(
        'courses_course_offering.id'), nullable=False)
    location_id = Column(Integer, ForeignKey(
        'places_location.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey(
        'people_person.id'), nullable=False)
    when = Column(DateTime, nullable=False)
    course_offering = relationship(
        'Course_Offering', backref='class_meeting', lazy=True)
    locations = relationship('Location', backref='meeting_location', lazy=True)
    person = relationship('Person', backref='teacher', lazy=True)
    students = relationship('Student', secondary=ClassAttendance,
                            back_populates='attendance', lazy=True)

    def __repr__(self):
        return f"<ClassMeeting(id={self.id})>"


class ClassMeetingSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    offering_id = fields.Integer(data_key='offeringId', required=True)
    location_id = fields.Integer(data_key='locationId', required=True)
    teacher_id = fields.Integer(data_key='teacherId', required=True)
    when = fields.DateTime(required=True)

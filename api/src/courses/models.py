from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Prerequisite

Prerequisite = Table('courses_prerequisite', Base.metadata,
                     Column('course_id', Integer, ForeignKey('courses_course.id'), primary_key=True),
                     Column('prereq_id', Integer, ForeignKey('courses_course.id'), primary_key=True))


# ---- DiplomaCourse

DiplomaCourse = Table('courses_diploma_course', Base.metadata,
                      Column('course_id', Integer, ForeignKey('courses_course.id'), primary_key=True),
                      Column('diploma_id', Integer, ForeignKey('courses_diploma.id'), primary_key=True))


# ---- DiplomaAwarded

class DiplomaAwarded(Base):
    __tablename__ = 'courses_diploma_awarded'
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)
    diploma_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses_diploma.id'), primary_key=True)
    when: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    students = relationship('Person', back_populates='diplomas_awarded', lazy=True)
    diplomas = relationship('Diploma', back_populates='diplomas_awarded', lazy=True)

    def __repr__(self):
        return f"<DiplomaAwarded(student_id={self.person_id},diploma_id={self.diploma_id})>"


class DiplomaAwardedCreate(BaseModel):
    personId: int
    diplomaId: int
    when: Optional[str] = None


class DiplomaAwardedRead(DiplomaAwardedCreate):
    model_config = ConfigDict(from_attributes=True)


class DiplomaAwardedSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'personId': obj.person_id,
            'diplomaId': obj.diploma_id,
            'when': str(obj.when) if obj.when else None,
        }

    def load(self, data, partial=False):
        return {
            'person_id': data.get('personId') or data.get('person_id'),
            'diploma_id': data.get('diplomaId') or data.get('diploma_id'),
            'when': data.get('when'),
        }


# ---- Class_Attendance

ClassAttendance = Table('courses_class_attendance', Base.metadata,
                        Column('class_id', Integer, ForeignKey('courses_class_meeting.id'), primary_key=True),
                        Column('student_id', Integer, ForeignKey('courses_students.id'), primary_key=True))


class ClassAttendanceSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'classId': obj.class_id,
            'studentId': obj.student_id,
        }


# ---- CourseCompletion

class CourseCompletion(Base):
    __tablename__ = 'courses_course_completion'
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses_course.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)

    people = relationship('Person', backref='completions', lazy=True)
    courses = relationship('Course', backref='completions', lazy=True)

    def __repr__(self):
        return f"<Course_Completion(course_id={self.course_id},person_id={self.person_id})>"


class CourseCompletionSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {'courseId': obj.course_id, 'personId': obj.person_id}

    def load(self, data, partial=False):
        return {
            'course_id': data.get('courseId') or data.get('course_id'),
            'person_id': data.get('personId') or data.get('person_id'),
        }


# ---- Course

class Course(Base):
    __tablename__ = 'courses_course'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    depends = relationship('Course', secondary=Prerequisite,
                           foreign_keys=[Prerequisite.c.course_id, Prerequisite.c.prereq_id],
                           primaryjoin=Prerequisite.c.prereq_id == id,
                           secondaryjoin=Prerequisite.c.course_id == id,
                           back_populates='prerequisites', lazy=True)
    prerequisites = relationship('Course', secondary=Prerequisite,
                                 primaryjoin=Prerequisite.c.course_id == id,
                                 secondaryjoin=Prerequisite.c.prereq_id == id,
                                 foreign_keys=[Prerequisite.c.course_id, Prerequisite.c.prereq_id],
                                 back_populates='depends', lazy=True)
    diplomas = relationship('Diploma', secondary=DiplomaCourse, back_populates='courses', lazy=True)
    images = relationship("ImageCourse", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id})>"


class CourseCreate(BaseModel):
    name: str
    description: str
    active: bool = True


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class CourseRead(CourseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        result = {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'active': obj.active,
        }
        if hasattr(obj, 'diplomaList') and obj.diplomaList is not None:
            result['diplomaList'] = [{'id': d.id, 'name': d.name} for d in obj.diplomaList]
        else:
            result['diplomaList'] = []
        return result

    def load(self, data, partial=False):
        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'active': data.get('active', True),
        }


# ---- Diploma

class Diploma(Base):
    __tablename__ = 'courses_diploma'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(StringTypes.LONG_STRING, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    courses = relationship('Course', secondary=DiplomaCourse, back_populates='diplomas', lazy=True)
    diplomas_awarded = relationship('DiplomaAwarded', back_populates='diplomas', lazy=True)

    def __repr__(self):
        return f"<Diploma(id={self.id})>"


class DiplomaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True


class DiplomaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class DiplomaRead(DiplomaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DiplomaSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        result = {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'active': obj.active,
        }
        if hasattr(obj, 'courseList') and obj.courseList is not None:
            result['courseList'] = [{'id': c.id, 'name': c.name} for c in obj.courseList]
        else:
            result['courseList'] = []
        if hasattr(obj, 'studentList') and obj.studentList is not None:
            result['studentList'] = [{'id': s.id} for s in obj.studentList]
        else:
            result['studentList'] = []
        return result

    def load(self, data, partial=False):
        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'active': data.get('active', True),
        }


# ---- Student

class Student(Base):
    __tablename__ = 'courses_students'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offering_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses_course_offering.id'), nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    courses_offered = relationship('Course_Offering', back_populates='students', lazy=True)
    person = relationship('Person', backref='students', lazy=True)
    attendance = relationship('ClassMeeting', secondary=ClassAttendance, back_populates='students', lazy=True)

    def __repr__(self):
        return f"<Student(id={self.id})>"


class StudentCreate(BaseModel):
    offeringId: int
    studentId: int
    confirmed: bool = False
    active: bool = True


class StudentRead(StudentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class StudentSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'offeringId': obj.offering_id,
            'studentId': obj.student_id,
            'confirmed': obj.confirmed,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return {
            'offering_id': data.get('offeringId') or data.get('offering_id'),
            'student_id': data.get('studentId') or data.get('student_id'),
            'confirmed': data.get('confirmed', False),
            'active': data.get('active', True),
        }


# ---- Course_Offering

class Course_Offering(Base):
    __tablename__ = 'courses_course_offering'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses_course.id'), nullable=False)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    max_size: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    students = relationship('Student', back_populates='courses_offered', lazy=True)
    course = relationship('Course', backref='courses_offered', lazy=True)

    def __repr__(self):
        return f"<Course_Offering(id={self.id})>"


class CourseOfferingCreate(BaseModel):
    courseId: Optional[int] = None
    description: str
    maxSize: int
    active: bool = True


class CourseOfferingRead(CourseOfferingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseOfferingSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'courseId': obj.course_id,
            'description': obj.description,
            'maxSize': obj.max_size,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return {
            'course_id': data.get('courseId') or data.get('course_id'),
            'description': data.get('description'),
            'max_size': data.get('maxSize') or data.get('max_size'),
            'active': data.get('active', True),
        }


# ---- ClassMeeting

class ClassMeeting(Base):
    __tablename__ = 'courses_class_meeting'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offering_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses_course_offering.id'), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('places_location.id'), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), nullable=False)
    when: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    course_offering = relationship('Course_Offering', backref='class_meeting', lazy=True)
    locations = relationship('Location', backref='meeting_location', lazy=True)
    person = relationship('Person', backref='teacher', lazy=True)
    students = relationship('Student', secondary=ClassAttendance, back_populates='attendance', lazy=True)

    def __repr__(self):
        return f"<ClassMeeting(id={self.id})>"


class ClassMeetingCreate(BaseModel):
    offeringId: int
    locationId: int
    teacherId: int
    when: datetime


class ClassMeetingRead(ClassMeetingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ClassMeetingSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'offeringId': obj.offering_id,
            'locationId': obj.location_id,
            'teacherId': obj.teacher_id,
            'when': obj.when.isoformat() if obj.when else None,
        }

    def load(self, data, partial=False):
        return {
            'offering_id': data.get('offeringId') or data.get('offering_id'),
            'location_id': data.get('locationId') or data.get('location_id'),
            'teacher_id': data.get('teacherId') or data.get('teacher_id'),
            'when': data.get('when'),
        }

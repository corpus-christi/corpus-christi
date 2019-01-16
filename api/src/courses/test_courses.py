import pytest
import random

from faker import Faker
from flask import url_for
from src.db import Base

from .models import Course, CourseSchema, Course_Offering, Class_Meeting,\
        Course_OfferingSchema, Diploma, DiplomaSchema, Student, StudentSchema,\
        Class_Meeting, Class_MeetingSchema, Diploma_Awarded, Diploma_AwardedSchema
from ..people.models import Person
from ..places.models import Location


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))

# --- Population Data

# --- Course

def course_object_factory():
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': flip()
    }
    return course

def course_object_factory_active():
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': True
    }
    return course

def course_object_factory_inactive():
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': False
    }
    return course

def create_multiple_courses(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()

def create_multiple_courses_active(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_active())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()

def create_multiple_courses_inactive(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_inactive())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()

# --- Course_Offering

def course_offerings_object_factory(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
    'maxSize': random.randint(1,100),
    'description': fake.paragraph(),
    'active': flip(),
    'courseId': course_id
    }
    return course_offerings

def course_offerings_object_factory_active(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
    'maxSize': random.randint(1,100),
    'description': fake.paragraph(),
    'active': True,
    'courseId': course_id
    }
    return course_offerings

def course_offerings_object_factory_inactive(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
    'maxSize': random.randint(1,100),
    'description': fake.paragraph(),
    'active': False,
    'courseId': course_id
    }
    return course_offerings

def create_multiple_course_offerings(sqla, n=3):
    """Commits the number of course offering to the DB."""
    course = sqla.query(Course).first()
    course_offerings_schema = Course_OfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(course_offerings_object_factory(course.id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()

def create_multiple_course_offerings_active(sqla, n=3):
    """Commits the number of course offering to the DB."""
    course = sqla.query(Course).first()
    course_offerings_schema = Course_OfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(course_offerings_object_factory_active(course.id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()

def create_multiple_course_offerings_inactive(sqla, n=3):
    """Commits the number of course offering to the DB."""
    course = sqla.query(Course).first()
    course_offerings_schema = Course_OfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(course_offerings_object_factory_inactive(course.id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()

# --- Prerequisites

def prerequisite_object_factory(course_id, prereq_id):
    """Cook up a fake prerequisite."""
    prerequisites = {
    'courseId': course_id,
    'prereqId': prereq_id
    }
    return prerequisites

def create_multiple_prerequisites(sqla):
    """Commits the courses - 1 number of prerequisites to the DB."""
    courses = sqla.query(Course).all()
    new_prerequisites = []
    for i in range(len(courses)-1):
        courses[i].prerequisites.append(courses[i+1])
        new_prerequisites.append(courses[i])
    sqla.add_all(new_prerequisites)
    sqla.commit()

# --- Diploma

def courses_diploma_object_factory():
    """Cook up a fake diploma."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_diploma = {
    'name': fake.sentence(nb_words=4),
    'description': fake.paragraph(),
    'active': flip()
    }
    return course_diploma

def create_multiple_diplomas(sqla, n=20):
    """Commits the number of diplomas to the DB."""
    courses = sqla.query(Course).all()
    course_diploma_schema = DiplomaSchema()
    new_courses = []
    for i in range(n):
        valid_course_diploma = course_diploma_schema.load(courses_diploma_object_factory())
        diploma = Diploma(**valid_course_diploma)
        courses[i%len(courses)].diplomas.append(diploma)
    sqla.add_all(new_courses)
    sqla.commit()

# --- Student

def student_object_factory(offering_id, student_id):
    """Cook up a fake student"""
    fake = Faker()
    course_student = {
    'studentId': student_id,
    'offeringId': offering_id,
    'confirmed': flip(),
    'active': flip()
    }
    return course_student

def create_multiple_students(sqla, n=6):
    """Commits the number of students to the DB."""
    students = sqla.query(Person).all()
    course_offering = sqla.query(Course_Offering).all()
    course_students_schema = StudentSchema()
    new_students = []
    for i in range(n):
        valid_student = course_students_schema.load(student_object_factory(course_offering[i%len(course_offering)].id, students[i%len(students)].id))
        student = Student(**valid_student)
        new_students.append(student)
    sqla.add_all(new_students)
    sqla.commit()

# --- Diploma_Award

def diploma_award_object_factory(diploma_id, student_id):
    """Cook up a fake diploma award"""
    fake = Faker()
    diploma_award = {
        'studentId': student_id,
        'diplomaId': diploma_id,
        'when': str(fake.past_date(start_date="-30d"))
    }
    return diploma_award

def create_diploma_awards(sqla, n):
    """Commits the number of diploma awards to the DB."""
    students = sqla.query(Student).all()
    diplomas = sqla.query(Diploma).all()
    diploma_award_schema = Diploma_AwardedSchema()
    new_diploma_awards = []
    for student in students:
        diploma = diplomas[random.randint(0,len(diplomas)-1)]
        valid_diploma_awarded = diploma_award_schema.load(diploma_award_object_factory(diploma.id,student.id))
        new_diploma_awards.append(Diploma_Awarded(**valid_diploma_awarded))
    sqla.add_all(new_diploma_awards)
    sqla.commit()

# --- Class_Meeting

def class_meeting_object_factory(teacher, offering_id, location=1):
    """Cook up a fake class meeting"""
    fake = Faker()
    class_meeting = {
    'offeringId': offering_id,
    'teacher': teacher,
    'when': str(fake.future_datetime(end_date="+30d")),
    'location': location,
    }
    return class_meeting

def create_class_meetings(sqla, n=6):
    """Commits the number of class meetings to the DB."""
    people = sqla.query(Person).all()
    course_offerings = sqla.query(Course_Offering).all()
    locations = sqla.query(Location).all()
    class_meeting_schema = Class_MeetingSchema()
    new_class_meetings = []
    for i in range(n):
        teacher = people[random.randint(0,len(people)-1)].id
        offering = course_offerings[i%len(course_offerings)].id
        location = locations[random.randint(0,len(locations)-1)].id

        valid_class_meeting = class_meeting_schema.load(class_meeting_object_factory(teacher, offering, location))
        class_meeting = Class_Meeting(**valid_class_meeting)
        new_class_meetings.append(class_meeting)
    sqla.add_all(new_class_meetings)
    sqla.commit()

# --- Class_Attendance

def create_class_attendance(sqla, n):
    """Commits the number of class attendances to the DB."""
    students = sqla.query(Student).all()
    class_meetings = sqla.query(Class_Meeting).all()
    new_class_attendance = []
    for i in range(n):
        class_meeting = class_meetings[random.randint(0, len(class_meetings)-1)]
        student = students[random.randint(0, len(students)-1)]
        student.attendance.append(class_meeting)
        new_class_attendance.append(student)
    sqla.add_all(new_class_attendance)
    sqla.commit()

# ---- Course

# Test course creation
def test_create_course(auth_client):
    # GIVEN course entry to put in database
    count = random.randint(8,19)
    # WHEN database does not contain entry
    for i in range(count):
        resp = auth_client.post(url_for('courses.create_course'), json=course_object_factory())
        assert resp.status_code == 201
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(Course).count() == count
    broken_course = {}
    resp = auth_client.post(url_for('courses.create_course'), json=broken_course)
    assert resp.status_code == 422

# Test getting all courses from the database
def test_read_all_courses(auth_client):
    # GIVEN existing (active and inactive) courses in database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_all_courses'))
    # THEN assert all entries from database are called
    assert len(resp.json) == count

#Test getting only active courses from the database
def test_read_all_active_courses(auth_client):
    # GIVEN existing and active courses
    count_active = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    active_courses = auth_client.sqla.query(Course).filter_by(active=True).all()
    # THEN assert all active courses are listed
    assert len(active_courses) == count_active

#Test getting only inactive courses from the database
def test_read_all_inactive_courses(auth_client):
    # GIVEN existing and inactive courses
    count_active = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    inactive_courses = auth_client.sqla.query(Course).filter_by(active=False).all()
    # THEN assert all active courses are listed
    assert len(inactive_courses) == count_inactive

# Test reading a single course from the database
def test_read_one_course(auth_client):
    # GIVEN one course in the database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    # WHEN call to database
    courses = auth_client.sqla.query(Course).all()
    # THEN assert entry called is only entry returned
    for course in courses:
        resp = auth_client.get(url_for('courses.read_one_course', course_id=course.id))
        # THEN we find a matching class
        assert resp.status_code == 200
        assert resp.json['name'] == course.name
        assert resp.json['description'] == course.description
        assert resp.json['active'] == course.active

#Test that active courses can be deactivated
def test_deactivate_course(auth_client):
    # GIVEN course to deactivate
    count = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course is changed to inactive
    for course in courses:
        resp = auth_client.patch(url_for('courses.deactivate_course', course_id=course.id),
            json={'active': False})
        # THEN assert course is inactive
        assert resp.status_code == 200
        assert resp.json['active'] == False

#Test that inactive courses can be reactivated
def test_reactivate_course(auth_client):
    # GIVEN course to activate
    count = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course is changed to active
    for course in courses:
        resp = auth_client.patch(url_for('courses.reactivate_course', course_id=course.id),
            json={'active': True})
        # THEN assert course is active
        assert resp.status_code == 200
        assert resp.json['active'] == True

"""
# Test
@pytest.mark.xfail()
def test_replace_course(auth_client):
    # GIVEN a deactivated course in database
    # WHEN
    # THEN assert
    assert True == False
"""

def test_update_course(auth_client):
    # GIVEN active or inactive course in database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course information updated
    for course in courses:
        resp = auth_client.patch(url_for('courses.update_course', course_id=course.id),
            json={'name':'test_name', 'description':'test_descr', 'active': False})
        # THEN assert course reflects new detail(s)
        print(resp)
        assert resp.status_code == 200
        assert resp.json['name'] == 'test_name'
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False

"""
@pytest.mark.xfail()
def test_delete_course(auth_client):
    # GIVEN undesirable course in database
    # WHEN course is removed
    # THEN assert course and all associated information deleted
    assert True == False
"""

# ---- Prerequisite

#Test that prerequisites can be added
def test_create_prerequisite(auth_client):
    # GIVEN existing and available course in database
    count = random.randint(2,13)
    create_multiple_courses(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    course = courses[0]
    prereq_ids = []
    for i in range(1,len(courses)-1):
        prereq_ids.append(courses[i].id)
    # WHEN course requires previous attendance to another course
    resp = auth_client.post(url_for('courses.create_prerequisite', course_id=course.id),
        json={ 'prerequisites': prereq_ids})
    assert resp.status_code == 201
    # THEN asssert course is prerequisite
    for i in range(len(prereq_ids)):
        assert auth_client.sqla.query(Course)[0].prerequisites[i].id == prereq_ids[i]

# This will test getting all prerequisites for all courses
def test_read_all_prerequisites(auth_client):
    # GIVEN existing and available course in database
    count_courses = random.randint(3,15)
    count_prereqs = count_courses - 1
    create_multiple_courses(auth_client.sqla, count_courses)
    # count_courses = auth_client.sqla.query(Course).count()
    count_prereqs = count_courses -1
    create_multiple_prerequisites(auth_client.sqla)
    # WHEN that course has prerequisites
    courses = auth_client.sqla.query(Course).all()
    prereqs = []
    for course in courses:
        for prereq in course.prerequisites:
            if prereq not in prereqs:
                prereqs.append(prereq)
    # THEN assert all prereq's are listed
    assert len(prereqs) == count_prereqs

#This will test getting prerequistes for one course
def test_read_one_course_prerequisites(auth_client):
    #GIVEN course in database
    count_courses = random.randint(3,15)
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    #WHEN that course has prerequisites
    courses = auth_client.sqla.query(Course).all()
    #THEN list all prerequisites of given course
    for i in range(len(courses)-1):
        assert courses[i].prerequisites == [courses[i+1]]


def test_update_prerequisite(auth_client):
    # GIVEN an existing and available course with an existing prereq
    count_courses = random.randint(3,13)
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    courses = auth_client.sqla.query(Course).all()
    # WHEN new prereq for existing course is required
    for course in courses:
        resp = auth_client.patch(url_for('courses.update_prerequisite', course_id=course.id),
            json={'prerequisites':[1]})
        assert resp.status_code == 200
    # THEN existing course has new prereq in place of existing prereq
    courses = auth_client.sqla.query(Course).all()
    for course in courses:
        if course.id == 1:
            continue
        assert course.prerequisites[0].id == 1

"""
@pytest.mark.xfail()
def test_delete_prerequisite(auth_client):
    # GIVEN an existing prereq and related course
    # WHEN prereq no longer needed from associated course
    # THEN prereq row entry removed (along with associated course)
    assert True == False
"""


# ---- Course_Offering

def test_create_course_offering(auth_client):
    # GIVEN an existing course
    count = random.randint(8,19)
    create_multiple_courses(auth_client.sqla, 1)
    course = auth_client.sqla.query(Course).first()
    # WHEN one or more courses need a section to offer
    for i in range(count):
        resp = auth_client.post(url_for('courses.create_course_offering'), json = course_offerings_object_factory(course.id))
        assert resp.status_code == 201
    # THEN create new course section
    assert auth_client.sqla.query(Course_Offering).count() == count

def test_read_all_course_offerings(auth_client):
    # GIVEN existing (active and inactive) course offerings
    create_multiple_courses(auth_client.sqla,1)
    count = random.randint(8,19)
    create_multiple_course_offerings(auth_client.sqla, count)
    # WHEN all sections needed
    course_offerings = auth_client.sqla.query(Course_Offering).all()
    # THEN list all course sections
    assert len(course_offerings) == count

def test_read_all_active_course_offerings(auth_client):
    # GIVEN existing active course offerings
    create_multiple_courses(auth_client.sqla,1)
    count_active = random.randint(3,11)
    create_multiple_course_offerings_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_course_offerings_inactive(auth_client.sqla, count_inactive)
    # WHEN all active course sections needed
    active_courses = auth_client.sqla.query(Course_Offering).filter_by(active=True).all()
    # THEN list all sections of active courses
    assert len(active_courses) == count_active

def test_read_all_inactive_course_offerings(auth_client):
    # GIVEN existing inactive course offerings
    create_multiple_courses(auth_client.sqla,1)
    count_active = random.randint(3,11)
    create_multiple_course_offerings_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_course_offerings_inactive(auth_client.sqla, count_inactive)
    # WHEN all inactive course sections needed
    inactive_courses = auth_client.sqla.query(Course_Offering).filter_by(active=False).all()
    # THEN list all sections of inactive courses
    assert len(inactive_courses) == count_inactive

def test_read_one_course_offering(auth_client):
    # GIVEN an existing course
    create_multiple_courses(auth_client.sqla,1)
    count = random.randint(3,11)
    create_multiple_course_offerings(auth_client.sqla, count)
    # WHEN one course section needed
    course_offerings = auth_client.sqla.query(Course_Offering).all()
    # THEN list one course section of course
    for course_offering in course_offerings:
        resp = auth_client.get(url_for('courses.read_one_course_offering',course_offering_id=course_offering.id))
        assert resp.status_code == 200
        assert resp.json['maxSize'] == course_offering.max_size
        assert resp.json['description'] == course_offering.description
        assert resp.json['active'] == course_offering.active
        assert resp.json['courseId'] == course_offering.course_id

"""
@pytest.mark.xfail()
def test_replace_course_offering(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
"""

def test_update_course_offering(auth_client):
    # GIVEN an existing (active or inactive) course offering
    create_multiple_courses(auth_client.sqla, 1)
    count = random.randint(3,11)
    create_multiple_course_offerings(auth_client.sqla, count)
    course_offerings = auth_client.sqla.query(Course_Offering).all()
    # WHEN course offering needs to update existing information
    for course_offering in course_offerings:
        resp = auth_client.patch(url_for('courses.update_course_offering', course_offering_id=course_offering.id),
            json={'max_size': 1, 'description':'test_descr', 'active':False})
        # THEN assert changes to course offering reflect update
        assert resp.status_code == 200
        assert resp.json['maxSize'] == 1
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False

"""
@pytest.mark.xfail()
def test_delete_course_offering(auth_client):
    # GIVEN an existing (active or inactive) course and at least one section
    # WHEN user desires to remove course offering
    # THEN
    assert True == False
"""

# ---- Prerequisite


@pytest.mark.xfail()
def test_create_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_prerequisites(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Diploma_Course


@pytest.mark.xfail()
def test_create_diploma_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_diploma_courses(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_diploma_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_diploma_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_diploma_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_diploma_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Diploma


@pytest.mark.xfail()
def test_create_diploma(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_diplomas(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_diploma(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_diploma(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_diploma(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_diploma(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Diploma_Awarded


@pytest.mark.xfail()
def test_create_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_diplomas_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Student


@pytest.mark.xfail()
def test_create_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_students(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Class_Attendance


@pytest.mark.xfail()
def test_create_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_class_attendance(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Class_Meeting


@pytest.mark.xfail()
def test_create_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_class_meetings(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


open

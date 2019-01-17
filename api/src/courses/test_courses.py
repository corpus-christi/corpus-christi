import pytest
import random

from faker import Faker
from flask import url_for
from src.db import Base

from .models import Course, CourseSchema, Course_Offering, Class_Meeting,\
        Course_OfferingSchema, Diploma, DiplomaSchema, Student, StudentSchema,\
        Class_Meeting, Class_MeetingSchema, Diploma_Awarded, Diploma_AwardedSchema,\
        Class_Attendance, Class_AttendanceSchema
from ..people.models import Person
from ..places.models import Location
from ..people.test_people import create_multiple_people


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
    'teacherId': teacher,
    'when': str(fake.future_datetime(end_date="+30d")),
    'locationId': location,
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
    """Test creating invalid course"""
    # GIVEN invalid course to put in database
    broken_course = {}
    # WHEN database queried
    resp = auth_client.post(url_for('courses.create_course'), json=broken_course)
    # THEN assert exception thrown
    assert resp.status_code == 422
    """Test creating valid course"""
    # GIVEN course entry to put in database
    count = random.randint(8,19)
    # WHEN database does not contain entry
    for i in range(count):
        resp = auth_client.post(url_for('courses.create_course'), json=course_object_factory())
        assert resp.status_code == 201
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(Course).count() == count

# Test getting all courses from the database
def test_read_all_courses(auth_client):
    """Test with empty database"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_courses'))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    # GIVEN existing (active and inactive) courses in database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_prerequisites(auth_client.sqla)
    create_multiple_course_offerings(auth_client.sqla, 5)
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_all_courses'))
    # THEN assert all entries from database are called
    assert resp.status_code == 200
    assert len(resp.json) == count

#Test getting courses by active state
def test_read_active_state_of_courses(auth_client):
    # GIVEN existing and active/inactive courses
    count_active = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    """Test listing all active courses"""
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_of_courses', active_state='active'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_active
    """Test listing all inactive courses"""
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_of_courses', active_state='inactive'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_inactive
    """Test listing courses with invalid state"""
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_of_courses', active_state='garbage'))
    # THEN assert error code
    assert resp.status_code == 404

# Test reading a single course from the database
def test_read_one_course(auth_client):
    """Test with invalid course"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_one_course', course_id = 1))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    # GIVEN one course in the database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_prerequisites(auth_client.sqla)
    create_multiple_course_offerings(auth_client.sqla, 5)
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

def test_update_course(auth_client):
    """Test with invalid course"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_course', course_id = 1))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
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

# ---- Prerequisite

#Test that prerequisites can be added
def test_create_prerequisite(auth_client):
    """Test with invalid course"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.post(url_for('courses.create_prerequisite', course_id = 1))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    # GIVEN existing and available course in database
    count = random.randint(2,13)
    create_multiple_courses(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    course = courses[0]
    prereq_ids = []
    for prereq in courses:
        prereq_ids.append(prereq.id)
    # WHEN course requires previous attendance to another course
    resp = auth_client.post(url_for('courses.create_prerequisite', course_id=course.id),
        json={ 'prerequisites': prereq_ids})
    assert resp.status_code == 201
    # THEN asssert course is prerequisite
    course = auth_client.sqla.query(Course).all()[0]
    for i in range(len(prereq_ids) - 1):
        assert course.prerequisites[i].id == prereq_ids[i+1]

# This will test getting all prerequisites for all courses
def test_read_all_prerequisites(auth_client):
    """Test with empty database"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_prerequisites'))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    # GIVEN existing and available course in database
    count_courses = random.randint(3,15)
    count_prereqs = count_courses - 1
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    # WHEN that course has prerequisites
    resp = auth_client.get(url_for('courses.read_all_prerequisites'))
    assert resp.status_code == 200
    # THEN assert all prereq's are listed
    assert len(resp.json) == count_prereqs

#This will test getting prerequistes for one course
def test_read_one_course_prerequisites(auth_client):
    """Test with invalid course"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_one_course_prerequisites', course_id = 1))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    #GIVEN course in database
    count_courses = random.randint(3,15)
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    #WHEN that course has prerequisites
    courses = auth_client.sqla.query(Course).all()
    #THEN list all prerequisites of given course
    for course in courses:
        resp = auth_client.get(url_for('courses.read_one_course_prerequisites', course_id=course.id))
        assert resp.status_code == 200
        for i in range(len(resp.json)):
            assert resp.json[i]['id'] == course.prerequisites[i].id
            assert resp.json[i]['name'] == course.prerequisites[i].name
            assert resp.json[i]['description'] == course.prerequisites[i].description
            assert resp.json[i]['active'] == course.prerequisites[i].active

def test_update_prerequisite(auth_client):
    """Test with invalid course"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_prerequisite', course_id = 1),
            json={'prerequisites':[1]})
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
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

# ---- Course_Offering

def test_create_course_offering(auth_client):
    """Test creating invalid course offering"""
    # GIVEN invalid course offering to put in database
    broken_course_offering = {}
    # WHEN database queried
    resp = auth_client.post(url_for('courses.create_course_offering'), json=broken_course_offering)
    # THEN assert exception thrown
    assert resp.status_code == 422
    """Test creating valid course offering"""
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
    """Test with empty database"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_course_offerings'))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
    # GIVEN existing (active and inactive) course offerings
    create_multiple_courses(auth_client.sqla,1)
    count = random.randint(8,19)
    create_multiple_course_offerings(auth_client.sqla, count)
    # WHEN all sections needed
    resp = auth_client.get(url_for('courses.read_all_course_offerings'))
    # THEN list all course sections
    assert len(resp.json) == count

def test_read_active_state_course_offerings(auth_client):
    # GIVEN existing active/inactive course offerings
    create_multiple_courses(auth_client.sqla,1)
    count_active = random.randint(3,11)
    create_multiple_course_offerings_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_course_offerings_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_course_offerings', active_state='active'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_active
    """Test listing all inactive courses"""
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_course_offerings', active_state='inactive'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_inactive
    """Test listing courses with invalid state"""
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_active_state_course_offerings', active_state='garbage'))
    # THEN assert error code
    assert resp.status_code == 404

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

def test_update_course_offering(auth_client):
    """Test with invalid course offering"""
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_course_offering', course_offering_id = 555))
    # THEN assert error code
    assert resp.status_code == 404
    """Test with populated database"""
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


# ---- Diploma_Course

@pytest.mark.xfail()
def test_create_diploma_course(client, db):
    # GIVEN a diploma ionm a database
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
def test_update_diploma_course(client, db):
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
def test_update_diploma(client, db):
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
def test_update_diploma_awarded(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

# ---- Student

student_schema = StudentSchema()

def setup_dependencies_of_student(auth_client, n):
    create_multiple_people(auth_client.sqla, n)
    create_multiple_courses_active(auth_client.sqla, n)
    create_multiple_course_offerings_active(auth_client.sqla, n)


@pytest.mark.student
def test_create_student(auth_client):
    setup_dependencies_of_student(auth_client,1)
    person = auth_client.sqla.query(Person).one()
    course_offering = auth_client.sqla.query(Course_Offering).one()
    # GIVEN an invalid student
    student = student_object_factory(course_offering.id, person.id)
    del student['confirmed']
    # WHEN requested to create student
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
    s_id=person.id), json=student)
    # THEN the response code should be 422
    assert resp.status_code == 422
    # GIVEN a course, course offering, and a valid person
    student = student_object_factory(course_offering.id, person.id)
    # WHEN a person wants to enroll in a course offering they become a student
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
        s_id=person.id), json=student)
    # THEN the person should be a student in that course
    course_offering = auth_client.sqla.query(Course_Offering).one()
    assert resp.status_code == 201
    assert course_offering.students[0].id == person.id
    # GIVEN a valid student that has been added to a course already
    student = student_object_factory(course_offering.id, person.id)
    # WHEN a person tries to register them again
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
        s_id=person.id), json=student)
    # THEN it will throw a 208 error
    assert resp.status_code == 208

@pytest.mark.xfail()
def test_read_all_students(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.student
def test_read_one_student(auth_client):
    # GIVEN a student is in the database
    create_multiple_people(auth_client.sqla, 1)
    create_multiple_courses(auth_client.sqla, 1)
    create_multiple_course_offerings(auth_client.sqla, 1)
    create_multiple_students(auth_client.sqla, 1)
    # WHEN that student needs to be read
    student = auth_client.sqla.query(Student).one()
    # THEN read that student
    resp = auth_client.get(url_for('courses.read_one_student', student_id=student.id))
    # assert resp == student.id
    print(resp)


@pytest.mark.xfail()
def test_replace_student(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

@pytest.mark.student
def test_update_student(auth_client):
    # GIVEN a student in the database
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    # WHEN that student needs to be updated
    student = auth_client.sqla.query(Student).one()
    attr = not student.confirmed
    # THEN assert these updates to the student
    resp = auth_client.patch(url_for('courses.update_student', student_id=student.id),
        json={"offering_id": 1, "student_id":student.id, "confirmed": attr, "active": False})
    assert resp.json['confirmed'] == attr
    student = auth_client.sqla.query(Student).one()
    assert student.confirmed == attr
    # GIVEN an invalid student_id
    student_id = 42
    # WHEN the id is updated to student
    resp = auth_client.patch(url_for('courses.update_student', student_id=student_id),
        json={"offering_id": 1, "student_id":student_id, "confirmed": True, "active": False})
    # THEN there should be a 404 error
    assert resp.status_code == 404

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
def test_update_class_attendance(client, db):
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
def test_update_class_meeting(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

open

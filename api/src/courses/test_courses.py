import pytest
import random

from faker import Faker
from flask import url_for

from .models import Course, CourseSchema, Course_Offering, Course_OfferingSchema, Diploma, DiplomaSchema


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def course_object_factory(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
        # 'id': course_id,
        'name': fake.sentence(nb_words=3),
        'description': fake.paragraph(),
        'active': flip()
    }
    return course

<<<<<<< HEAD
def course_object_factory_active(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': True
    }
    return course

def course_object_factory_inactive(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': False
    }
    return course
=======
>>>>>>> feature/courses-33_creating-a-new-course

def create_multiple_courses(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
<<<<<<< HEAD
<<<<<<< HEAD
        valid_course = course_schema.load(course_object_factory(i))
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()
    print(new_courses)

def create_multiple_courses_active(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_active(i))
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()
    print(new_courses)

def create_multiple_courses_inactive(sqla, n=10):
    """Commits the number of courses to the DB."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_inactive(i))
        course_model = Course(**valid_course)
        new_courses.append(course_model)
=======
        valid_course = course_schema.load(course_object_factory())
=======
        valid_course = course_schema.load(course_object_factory(i))
>>>>>>> feature/courses-33_creating-a-new-course
        new_courses.append(Course(**valid_course))
>>>>>>> feature/courses-33_creating-a-new-course-ui
    sqla.add_all(new_courses)
    sqla.commit()


def course_offerings_object_factory(course_id):
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
        'maxSize': random.randint(1, 100),
        'description': fake.paragraph(),
        'active': flip(),
        'courseId': course_id
    }
    return course_offerings


def create_multiple_course_offerings(sqla, n=3):
    """Commits the number of course offering to the DB."""
    courses = sqla.query(Course).all()
    course_offerings_schema = Course_OfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(
            course_offerings_object_factory(courses[i].id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()


def create_multiple_prerequisites(sqla):
    """Commits the number of prerequisites to the DB."""
    courses = sqla.query(Course).all()
    new_prerequisites = []
    for i in range(len(courses)-1):
        courses[i].prerequisites = [courses[i+1]]
    sqla.add_all(new_prerequisites)
    sqla.commit()


def courses_diploma_object_factory():
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_diploma = {
    'name': fake.sentence(nb_words=4),
    'description': fake.paragraph(),
    'active': flip(),
    }
    return course_diploma


def create_multiple_diplomas(sqla, n=20):
    """Commits the number of course offering to the DB."""
    courses = sqla.query(Course).all()
    course_diploma_schema = DiplomaSchema()
    new_courses = []
    for i in range(20):
        valid_course_diploma = course_diploma_schema.load(courses_diploma_object_factory())
        valid_diploma = Diploma(**valid_course_diploma)
        courses[i%len(courses)].diploma.append(valid_diploma)
    sqla.add_all(new_courses)
    sqla.commit()


# ---- Course

# Test course creation
<<<<<<< HEAD
def test_create_course(auth_client):
=======


@pytest.mark.xfail()
def test_create_course(client, db):
>>>>>>> feature/courses-33_creating-a-new-course
    # GIVEN course entry to put in database
    count = random.randint(8,19)
    create_multiple_courses(auth_client.sqla, count)
    # WHEN database does not contain entry
    courses = auth_client.sqla.query(Course).all()
    # THEN assert that entry is now in database
<<<<<<< HEAD
    assert len(courses) == count
    
=======
    assert True == False

>>>>>>> feature/courses-33_creating-a-new-course-ui
# Test getting all courses from the database
<<<<<<< HEAD
def test_read_all_courses(auth_client):
=======


@pytest.mark.xfail()
def test_read_all_courses(client, db):
>>>>>>> feature/courses-33_creating-a-new-course
    # GIVEN existing (active and inactive) courses in database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    # WHEN call to database
    courses = auth_client.sqla.query(Course).all()
    # THEN assert all entries from database are called
    assert len(courses) == count

<<<<<<< HEAD
#Test getting only active courses from the database
def test_read_all_active_courses(auth_client):
=======

@pytest.mark.xfail()
def test_read_all_active_courses(client, db):
>>>>>>> feature/courses-33_creating-a-new-course
    # GIVEN existing and active courses
    count_active = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    active_courses = auth_client.sqla.query(Course).filter_by(active=True).all()
    # THEN assert all active courses are listed
    assert len(active_courses) == count_active

<<<<<<< HEAD
#Test getting only inactive courses from the database
def test_read_all_inactive_courses(auth_client):
=======

@pytest.mark.xfail()
def test_read_all_inactive_courses(client, db):
>>>>>>> feature/courses-33_creating-a-new-course
    # GIVEN existing and inactive courses
    count_active = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    inactive_courses = auth_client.sqla.query(Course).filter_by(active=False).all()
    # THEN assert all active courses are listed
<<<<<<< HEAD
    assert len(inactive_courses) == count_inactive
    
=======
    assert True == False

>>>>>>> feature/courses-33_creating-a-new-course-ui
# Test reading a single course from the database
<<<<<<< HEAD
def test_read_one_course(auth_client):
=======


@pytest.mark.xfail()
def test_read_one_course(client, db):
>>>>>>> feature/courses-33_creating-a-new-course
    # GIVEN one course in the database
    count = random.randint(3,11)
    create_multiple_courses(auth_client.sqla, count)
    # WHEN call to database
<<<<<<< HEAD
    courses = auth_client.sqla.query(Course).all()
    # THEN assert entry called is only entry returned 
    for course in courses:
        resp = auth_client.get(url_for('courses.read_one_course', course_id=course.id)) 
        # THEN we find a matching class
        assert resp.status_code == 200
        assert resp.json['name'] == course.name
        assert resp.json['description'] == course.description
        assert resp.json['active'] == course.active
=======
    # THEN assert entry called is only entry returned
    assert True == False
>>>>>>> feature/courses-33_creating-a-new-course-ui

<<<<<<< HEAD
#Test that active courses can be deactivated
=======

def create_course(sqla):
    """Create single course into DB"""
    course_schema = CourseSchema()
    new_courses = []
    valid_course = course_schema.load(course_object_factory(1))
    new_courses.append(Course(**valid_course))
    sqla.add_all(new_courses)  # should only add one course tho
    sqla.commit()


>>>>>>> feature/courses-33_creating-a-new-course
@pytest.mark.smoke
def test_deactivate_course(auth_client):
    # GIVEN course to deactivate
    count = random.randint(3,11)
    create_multiple_courses_active(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course is changed to inactive
<<<<<<< HEAD
    for course in courses:
        resp = auth_client.patch(url_for('courses.deactivate_course', course_id=course.id), json={'active': False})
        # THEN assert course is inactive
        assert resp.status_code == 200
        assert resp.json['active'] == False

#Test that inactive courses can be reactivated
=======
    resp = auth_client.patch(url_for('courses.deactivate_course', course_id=course.id),
                             json={'active': False})
    # THEN assert course is inactive
    assert resp.status_code == 200
    assert resp.json['active'] == False


>>>>>>> feature/courses-33_creating-a-new-course
@pytest.mark.smoke
def test_reactivate_course(auth_client):
    # GIVEN course to activate
    count = random.randint(3,11)
    create_multiple_courses_inactive(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course is changed to active
<<<<<<< HEAD
    for course in courses:
        resp = auth_client.patch(url_for('courses.reactivate_course', course_id=course.id), json={'active': True})
        # THEN assert course is active
        assert resp.status_code == 200
        assert resp.json['active'] == True
=======
    resp = auth_client.patch(url_for('courses.reactivate_course', course_id=course.id),
                             json={'active': True})
    # THEN assert course is active
    assert resp.status_code == 200
    assert resp.json['active'] == True
>>>>>>> feature/courses-33_creating-a-new-course


"""
# Test
@pytest.mark.xfail()
def test_replace_course(auth_client):
    # GIVEN a deactivated course in database
    # WHEN
    # THEN assert
    assert True == False
"""


@pytest.mark.xfail()
def test_update_course(auth_client):
    # GIVEN active or inactive course in database
    # WHEN course information updated
    # THEN assert course reflects new detail(s)
    assert True == False


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
    create_multiple_courses(auth_client.sqla, 2)
    prereq = auth_client.sqla.query(Course).first()
    course = auth_client.sqla.query(Course).all()[-1]
    # WHEN course requires previous attendance to another course
<<<<<<< HEAD
    resp = auth_client.patch(url_for('courses.create_prerequisite', course_idcd=course.id), json={'prerequisite':[prereq.id]})
    # THEN asssert course is prerequisite
    assert resp.status_code == 200
    assert resp.json['prereq_id'] == prereq.id
    
=======
    # THEN add course as prerequisite
    assert True == False

>>>>>>> feature/courses-33_creating-a-new-course-ui
# This will test getting all prerequisites for a single course


@pytest.mark.xfail()
def test_read_all_prerequisites(auth_client):
    # GIVEN existing and available course in database
    # WHEN that course has prerequisites
    # THEN assert all prereq's are listed
    assert True == False

# FIX NAME (Will test to see all courses that have given course as a prerequisite)


@pytest.mark.xfail()
<<<<<<< HEAD
def test_read_all_courses_with_prerequisite(auth_client):
    #GIVEN prerequisite course in database
    #WHEN other courses have that course as a prerequisite
    #THEN list all courses with given prerequisite
    assert True == False

<<<<<<< HEAD
=======



>>>>>>> feature/courses-33_creating-a-new-course-ui
=======
def test_read_all_courses_with_prerequisite(client, db):
    # GIVEN prerequisite course in database
    # WHEN other courses have that course as a prerequisite
    # THEN list all courses with given prerequisite
    assert True == False


>>>>>>> feature/courses-33_creating-a-new-course
@pytest.mark.xfail()
def test_update_prerequisite(auth_client):
    # GIVEN an existing and available course with an existing prereq
    # WHEN new prereq for existing course is required
    # THEN existing course has new prereq in place of existing prereq
    assert True == False


"""
@pytest.mark.xfail()
def test_delete_prerequisite(auth_client):
    # GIVEN an existing prereq and related course
    # WHEN prereq no longer needed from associated course
    # THEN prereq row entry removed (along with associated course)
    assert True == False
"""


# ---- Course_Offering


@pytest.mark.xfail()
def test_create_course_offering(auth_client):
    # GIVEN an existing course
    # WHEN one or more courses need a section to offer
    # THEN create new course section
    assert True == False


@pytest.mark.xfail()
def test_read_all_course_offerings(auth_client):
    # GIVEN existing (active and inactive) course offerings
    # WHEN all sections needed
    # THEN list all course sections
    assert True == False


@pytest.mark.xfail()
def test_read_all_active_course_offerings(auth_client):
    # GIVEN existing active course offerings
    # WHEN all active course sections needed
    # THEN list all sections of active courses
    assert True == False


@pytest.mark.xfail()
def test_read_all_inactive_course_offerings(auth_client):
    # GIVEN existing inactive course offerings
    # WHEN all inactive course sections needed
    # THEN list all sections of inactive courses
    assert True == False


@pytest.mark.xfail()
def test_read_one_course_offering(auth_client):
    # GIVEN an existing course
    # WHEN one course section needed
    # THEN list one course section of course
    assert True == False


"""
@pytest.mark.xfail()
def test_replace_course_offering(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
"""


@pytest.mark.xfail()
<<<<<<< HEAD
def test_update_course_offering(auth_client):
    # GIVEN an existing (active or inactive) course offering 
=======
def test_update_course_offering(client, db):
    # GIVEN an existing (active or inactive) course offering
>>>>>>> feature/courses-33_creating-a-new-course-ui
    # WHEN course offering needs to update existing information
    # THEN assert changes to course offering reflect update
    assert True == False


"""
@pytest.mark.xfail()
def test_delete_course_offering(auth_client):
    # GIVEN an existing (active or inactive) course and at least one section
    # WHEN user desires to remove course offering
    # THEN
    assert True == False
"""
<<<<<<< HEAD
    
open 
=======
>>>>>>> feature/courses-33_creating-a-new-course-ui

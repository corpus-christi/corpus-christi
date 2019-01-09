import pytest
import random

from faker import Faker

from .models import Course, CourseSchema, Prerequisite, PrerequisiteSchema

def flip():
    """Return true or false randomly."""
    return random.choice((True, False))

def course_object_factory():
    """Cook up a fake course."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
    'name': fake.sentence(nb_words=3),
    'description': fake.paragraph(),
    'active': flip()
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
        # course_model.
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()


# ---- Course


@pytest.mark.xfail()
def test_create_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_courses(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_course(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Prerequisite


@pytest.mark.xfail()
def test_create_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_course_offerings(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

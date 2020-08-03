import os

import pytest
from src import db, create_app
from src.courses.models import Course, Diploma
from src.i18n.models import Language, I18NValue
from src.people.models import Role
from src.places.models import Country

from commands.people import create_account_cli
from commands.app import create_app_cli
from commands.courses import create_course_cli
from commands.events import create_event_cli
from commands.faker import create_faker_cli


@pytest.fixture
def runner():
    app = create_app(os.getenv('CC_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out

    db.drop_all()
    db.create_all()

    create_account_cli(app)
    create_app_cli(app)
    create_course_cli(app)
    create_event_cli(app)
    create_faker_cli(app)

    yield app.test_cli_runner()


def test_load_counties(runner):
    runner.invoke(args=['app', 'load-countries'])
    assert db.session.query(Country).count() > 0


def test_load_languages(runner):
    runner.invoke(args=['app', 'load-languages'])
    assert db.session.query(Language).count() > 0


def test_load_roles(runner):
    assert db.session.query(Role).count() == 0
    runner.invoke(args=['app', 'load-roles'])
    assert db.session.query(Role).count() > 0


# ---- Course CLI


def test_course_cli(runner):
    """Tests the cli command for creating a course"""
    # GIVEN all the valid required arguments for course
    name = 'course1'
    desc = 'description'
    # WHEN call is invoked
    runner.invoke(args=['courses', 'create-course', name, desc])
    # THEN a course with zero prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert course.prerequisites == []
    # GIVEN all the valid arguments for course and a prereqs
    name = 'course2'
    prereq = 'course1'
    # WHEN call is invoked
    runner.invoke(args=['courses', 'create-course', name, desc, '--prereq', prereq])
    # THEN a course with two prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert len(course.prerequisites) == 1
    assert course.prerequisites[0].name == prereq
    # GIVEN offering flag for a course
    name = 'course4'
    offering_name = 'course1'
    # WHEN call is invoked
    runner.invoke(args=['courses', 'create-course', name, desc, '--offering', offering_name])
    # THEN help message is printed
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert course.courses_offered[0].description == offering_name


def test_diploma_cli(runner):
    """Tests the cli command for creating a diploma"""
    # GIVEN all the valid arguments for a diploma
    name = 'diploma1'
    desc = 'description'
    # WHEN call is invoked
    runner.invoke(args=['courses', 'create-diploma', name, desc])
    # THEN
    diploma = db.session.query(Diploma).filter_by(name=name).first()
    assert diploma.name == name
    assert diploma.description == desc
    # GIVEN missing arguments for diploma
    name = 'diploma2'
    # WHEN call is invoked
    result = runner.invoke(args=['courses', 'create-diploma'])
    # THEN help message is printed
    assert 'Usage' in result.output


def test_load_attribute_types(runner):
    runner.invoke(args=['app', 'load-attribute-types'])
    assert db.session.query(I18NValue).filter(
        I18NValue.key_id == 'attribute.date').count() > 0

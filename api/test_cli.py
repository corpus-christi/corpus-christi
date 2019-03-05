import math
import random
import click
import os
import pytest

from src.people.models import Person, Account, Role
from src.courses.models import Course, Diploma
from src.places.models import Country
from src.i18n.models import Language, I18NLocale, I18NValue
from src import db, create_app

ccapi = __import__("cc-api")


@pytest.fixture
def init_app():
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out

    db.drop_all()
    db.create_all()


def test_load_counties():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_countries)
    assert db.session.query(Country).count() > 0


def test_load_languages():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_languages)
    assert db.session.query(Language).count() > 0


def test_load_roles():
    init_app()
    assert db.session.query(Role).count() == 0
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_roles)
    assert db.session.query(Role).count() > 0

# ---- Course CLI


def test_course_cli():
    """Tests the cli command for creating a course"""
    runner = ccapi.app.test_cli_runner()
    # GIVEN all the valid required arguments for course
    name = 'course1'
    # WHEN call is invoked
    runner.invoke(ccapi.create_course, [name, ''])
    # THEN a course with zero prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert course.prerequisites == []
    # # GIVEN all the valid arguments for course and a prereqs
    name = 'course2'
    prereq = 'course1'
    # WHEN call is invoked
    runner.invoke(ccapi.create_course, [name, '', '--prereq', prereq])
    # THEN a course with two prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert len(course.prerequisites) == 1
    assert course.prerequisites[0].name == prereq
    # GIVEN offering flag for a course
    name = 'course4'
    offering_name = 'course1'
    # WHEN call is invoked
    result = runner.invoke(ccapi.create_course, [
                           name, '', '--offering', offering_name])
    # THEN help message is printed
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert course.courses_offered[0].description == offering_name


def test_diploma_cli():
    """Tests the cli command for creating a diploma"""
    runner = ccapi.app.test_cli_runner()
    # GIVEN all the valid arguments for a diploma
    name = 'diploma1'
    # WHEN call is invoked
    runner.invoke(ccapi.create_diploma, [name, ''])
    # THEN
    diploma = db.session.query(Diploma).filter_by(name=name).first()
    assert diploma.name == name
    assert diploma.description == ''
    # GIVEN missing arguments for diploma
    name = 'diploma2'
    # WHEN call is invoked
    result = runner.invoke(ccapi.create_diploma, [name])
    # THEN help message is printed
    assert 'Usage' in result.output


def test_load_attribute_types():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_attribute_types)
    assert db.session.query(I18NValue).filter(
        I18NValue.key_id == 'attribute.date').count() > 0

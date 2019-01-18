import math
import random

from src.people.models import Person, Account, Role
from src.places.models import Country
from src.courses.models import Course
from src.i18n.models import Language, I18NLocale, I18NValue
from src import db

ccapi = __import__("cc-api")


def test_load_counties():
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_countries)
    assert db.session.query(Country).count() > 0


def test_load_languages():
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_languages)
    assert db.session.query(Language).count() > 0


def test_load_roles():
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
    runner.invoke(ccapi.create_account, [name,''])
    # THEN a course with zero prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert course.prerequisites == []
    # GIVEN all the valid arguments for course and 2 prereqs
    name = 'course2'
    num_prereqs = 2
    # WHEN call is invoked
    runner.invoke(ccapi.create_account, [name, '', '--prereq', num_prereqs])
    # THEN a course with two prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert len(course.prerequisites) == num_prereqs
    # GIVEN missing arguments for course
    name = 'course3'
    # WHEN call is invoked
    result = runner.invoke(ccapi.create_account, [name])
    # THEN help message is printed
    assert 'Usage' in result.output

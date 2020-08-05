import os

import pytest
import json
from src import db, create_app
from src.courses.models import Course, Diploma
from src.i18n.models import Language, I18NValue, I18NLocale, I18NKey
from src.people.models import Role
from src.places.models import Country

from commands.people import create_account_cli
from commands.app import create_app_cli
from commands.courses import create_course_cli
from commands.events import create_event_cli
from commands.faker import create_faker_cli
from commands.i18n import create_i18n_cli


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
    create_i18n_cli(app)

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
    runner.invoke(
        args=[
            'courses',
            'create-course',
            name,
            desc,
            '--prereq',
            prereq])
    # THEN a course with two prereqs is created
    course = db.session.query(Course).filter_by(name=name).first()
    assert course.name == name
    assert len(course.prerequisites) == 1
    assert course.prerequisites[0].name == prereq
    # GIVEN offering flag for a course
    name = 'course4'
    offering_name = 'course1'
    # WHEN call is invoked
    runner.invoke(
        args=[
            'courses',
            'create-course',
            name,
            desc,
            '--offering',
            offering_name])
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

# ---- i18n CLI


def test_i18n_load(runner):
    with runner.isolated_filesystem():
        filename = 'en-US.json'
        # GIVEN a file with some translation entries
        with open(filename, "w") as f:
            json.dump({
                "account": {
                    "messages": {
                        "added-ok": {
                            "gloss": "Account added successfully",
                            "verified": False
                        },
                        "updated-ok": {
                            "gloss": "Account updated successfully",
                            "verified": False
                        }
                    }
                }
            }, f)
            # WHEN we load the entries into the database
        result = runner.invoke(
            args=[
                'i18n',
                'load',
                'en-US',
                '--target',
                filename])
        # THEN we expect the correct number of entries to be loaded
        assert db.session.query(I18NValue).count() == 2


def test_i18n_dump(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    db.session.add_all([I18NLocale(**d) for d in locale_data])
    db.session.add_all([I18NKey(**k) for k in key_data])
    db.session.add_all([
        I18NValue(
            locale_code=locale['code'],
            key_id=key['id'],
            gloss=f"{key['desc']} in {locale['desc']}")
        for locale in locale_data for key in key_data
    ])
    db.session.commit()
    assert db.session.query(I18NValue).count() == 3
    with runner.isolated_filesystem():
        # WHEN we dump the entries into a file
        filename = 'en-US.json'
        result = runner.invoke(
            args=[
                'i18n',
                'dump',
                'en-US',
                '--target',
                filename])
        # THEN we expect the file to be created
        assert os.path.exists(filename)
        # THEN we expect the json structure to match what we created
        with open(filename, "r") as f:
            tree = json.load(f)
            assert 'alt' in tree
            assert 'app' in tree
            assert tree['app']['desc']['gloss'] == "This is a test application in English US"

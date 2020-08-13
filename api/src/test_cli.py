import os

import pytest
import json
import yaml
from . import db
from .courses.models import Course, Diploma
from .i18n.models import Language, I18NValue, I18NLocale, I18NKey
from .people.models import Role
from .places.models import Country


def test_load_countries(runner):
    result = runner.invoke(args=['app', 'load-countries'])
    assert db.session.query(Country).count() > 0


def test_load_languages(runner):
    result = runner.invoke(args=['app', 'load-languages'])
    assert db.session.query(Language).count() > 0


def test_load_roles(runner):
    assert db.session.query(Role).count() == 0
    result = runner.invoke(args=['app', 'load-roles'])
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


def populate_database_i18n(locale_data, key_data):
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
    assert db.session.query(I18NValue).count() == len(
        locale_data) * len(key_data)


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


def test_i18n_load_descriptions(runner):
    with runner.isolated_filesystem():
        filename = 'en-US.json'
        # GIVEN a file with some descriptions
        with open(filename, "w") as f:
            json.dump({
                "actions": {
                    "activate-account": "Activate account",
                    "add-address": "Add a new address",
                },
                "courses": {
                    "info-meeting-dates": "Inform the user they can select multiple dates for a class meeting",
                }
            }, f)
            # WHEN we load the descriptions into the database
        result = runner.invoke(
            args=[
                'i18n',
                'load-descriptions',
                '--target',
                filename])
        # THEN we expect the correct number of keys to be loaded
        assert db.session.query(I18NKey).count() == 3
        # THEN we expect the right description to be in the database
        key = db.session.query(I18NKey).filter_by(
            id="actions.add-address").first()
        assert key is not None
        assert key.desc == "Add a new address"

        # WHEN we try to override some data without the override flag
        with open(filename, "w") as f:
            json.dump({
                "actions": {
                    "add-address": "An action to add a new address",
                },
            }, f)
        result = runner.invoke(
            args=[
                'i18n',
                'load-descriptions',
                '--no-override',
                '--target',
                filename])
        # THEN we expect nothing to be changed
        key = db.session.query(I18NKey).filter_by(
            id="actions.add-address").first()
        assert key is not None
        assert key.desc == "Add a new address"
        # THEN we expect a hint in the output
        assert b"Hint" in result.stdout_bytes
        assert b"use --override" in result.stdout_bytes

        # WHEN we try to override some data with the override flag
        result = runner.invoke(
            args=[
                'i18n',
                'load-descriptions',
                '--override',
                '--target',
                filename])
        # THEN we expect the description to be changed
        key = db.session.query(I18NKey).filter_by(
            id="actions.add-address").first()
        assert key is not None
        assert key.desc == "An action to add a new address"


def test_i18n_dump(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
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


def test_i18n_dump_descriptions(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'}]
    key_data = [
        {'id': 'groups.name', 'desc': ''},
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    with runner.isolated_filesystem():
        # WHEN we dump the descriptions into a file
        filename = 'en-US.json'
        result = runner.invoke(
            args=[
                'i18n',
                'dump-descriptions',
                '--target',
                filename])
        # THEN we expect the file to be created
        assert os.path.exists(filename)
        # THEN we expect descriptions to match what we created
        with open(filename, "r") as f:
            tree = json.load(f)
            assert 'alt' in tree
            assert tree['alt']['logo'] == 'Alt text for logo'

        # WHEN we dump the descriptions without empty entries
        result = runner.invoke(
            args=[
                'i18n',
                'dump-descriptions',
                '--no-dump-empty',
                '--target',
                filename])
        # THEN we expect the empty entries to be ommitted
        with open(filename, "r") as f:
            tree = json.load(f)
            assert 'groups' not in tree

        # WHEN we dump the descriptions with empty entries and with a
        # placeholder
        result = runner.invoke(
            args=[
                'i18n',
                'dump-descriptions',
                '--dump-empty',
                '--empty-placeholder',
                'no description available',
                '--target',
                filename])
        # THEN we expect the empty entries to contain the placeholder
        with open(filename, "r") as f:
            tree = json.load(f)
            assert 'groups' in tree
            assert tree['groups']['name'] == 'no description available'


def test_i18n_import(runner):
    with runner.isolated_filesystem():
        filename = 'entries.yaml'
        # GIVEN a file with "locale-tail" structured tree
        with open(filename, "w") as f:
            f.write("""added-ok:
  _desc: messages for successful adding account
  en-US: Account added successfully
  es-EC: Cuenta agregada exitosamente
updated-ok:
  _desc: messages for successful updating account
  en-US: Account updated successfully
  es-EC: "Cuenta actualizada con \xE9xito" """)
        # WHEN we load the entries into the database
        result = runner.invoke(
            args=['i18n',
                  'import',
                  '--target',
                  filename,
                  'account.messages'])
        # THEN we expect the correct number of entries to be loaded
        assert db.session.query(I18NValue).count() == 4
        # THEN we expect the value to be correct
        assert db.session.query(I18NValue).filter_by(
            key_id="account.messages.added-ok",
            locale_code='en-US').first().gloss == "Account added successfully"
        # THEN we expect the descriptions to be loaded correctly
        assert db.session.query(I18NKey).filter_by(
            id="account.messages.added-ok").first().desc == "messages for successful adding account"

        # WHEN we update a single leaf record with standard input
        result = runner.invoke(
            args=[
                'i18n',
                'import',
                '--target',
                '-',
                'account.messages.added-ok'],
            input="_desc: Messages for successful adding account\nen-US: Success!")
        # THEN we expect the record to be updated
        assert db.session.query(I18NValue).filter_by(
            key_id="account.messages.added-ok",
            locale_code='en-US').first().gloss == "Success!"
        # THEN we expect the descriptions to be loaded correctly
        assert db.session.query(I18NKey).filter_by(
            id="account.messages.added-ok").first().desc == "Messages for successful adding account"
        # WHEN we try to write a leaf record onto an intermediate path
        result = runner.invoke(
            args=[
                'i18n',
                'import',
                '--target',
                '-',
                'account.messages'],
            input="_desc: Messages for successful adding account\nen-US: Success!")

        # THEN we expect the program to be aborted
        assert result.exit_code == 1
        # THEN we expect the correct output is printed
        assert b'invalid locale-tail structured tree' in result.stdout_bytes

        # WHEN we try to write a leaf node without a path
        result = runner.invoke(
            args=[
                'i18n',
                'import',
                '--target',
                '-'],
            input="_desc: Messages for successful adding account\nen-US: Success!")

        # THEN we expect the program to be aborted
        assert result.exit_code == 2
        # THEN we expect the correct output is printed
        assert b'Must specify a path when overriding with a leaf node' in result.stdout_bytes


def test_i18n_export(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'},
                   {'code': 'es-EC', 'desc': 'Spanish Ecuador'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    with runner.isolated_filesystem():
        # WHEN we export all the entries into a file
        filename = 'entries.yaml'
        result = runner.invoke(
            args=[
                'i18n',
                'export',
                '--target',
                filename])
        # THEN we expect the file to be created
        assert os.path.exists(filename)
        # THEN we expect the json structure to match what we created
        with open(filename, "r") as f:
            tree = yaml.safe_load(f)
            assert 'alt' in tree
            assert 'app' in tree
            assert tree['app']['desc']['en-US'] == "This is a test application in English US"

        # WHEN we export part of the entries into a file
        filename = 'entries.yaml'
        result = runner.invoke(
            args=[
                'i18n',
                'export',
                '--target',
                filename,
                'app'])
        # THEN we expect the json structure to match what we created
        with open(filename, "r") as f:
            tree = yaml.safe_load(f)
            assert 'name' in tree
            assert 'desc' in tree
            assert tree['desc']['en-US'] == "This is a test application in English US"


def test_i18n_list(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'},
                   {'code': 'es-EC', 'desc': 'Spanish Ecuador'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    # WHEN we list some entries
    result = runner.invoke(
        args=[
            'i18n',
            'list',
            'app'])
    list_result = result
    # THEN we expect the same output as export
    result = runner.invoke(
        args=[
            'i18n',
            'export',
            '--target',
            '-',
            'app'])
    assert result.stdout_bytes == list_result.stdout_bytes


def test_i18n_add(runner):
    # GIVEN an empty database
    # WHEN we add an entry
    result = runner.invoke(
        args=[
            'i18n',
            'add',
            'en-US',
            'some.path',
            'gloss'
        ])
    # THEN we expect the entry to be added in the database
    values = db.session.query(I18NValue).all()
    assert len(values) == 1
    value = values[0]
    assert value.key_id == 'some.path'
    assert value.gloss == 'gloss'
    assert value.locale_code == 'en-US'

    # WHEN we add the entry again
    result = runner.invoke(
        args=[
            'i18n',
            'add',
            'en-US',
            'some.path',
            'new gloss'
        ])
    # THEN we expect the output to contain a warning
    assert b"already exists" in result.stdout_bytes
    # THEN we expect nothing to be changed
    values = db.session.query(I18NValue).all()
    assert len(values) == 1
    value = values[0]
    assert value.gloss == 'gloss'


def test_i18n_update(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    # WHEN we update an entry
    result = runner.invoke(
        args=[
            'i18n',
            'update',
            'en-US',
            'app.name',
            'new gloss'
        ])
    # THEN we expect the entry to be updated in the database
    value = db.session.query(I18NValue).filter_by(
        key_id='app.name', locale_code='en-US').first()
    assert value is not None
    assert value.gloss == 'new gloss'

    # WHEN we update a non-existent entry
    result = runner.invoke(
        args=[
            'i18n',
            'update',
            'en-US',
            'some.random.path.that.does.not.exist',
            'new gloss'
        ])
    # THEN we expect the output to contain a warning
    assert b"does not exist" in result.stdout_bytes


def test_i18n_delete(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'},
                   {'code': 'es-EC', 'desc': 'Spanish Ecuador'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    # WHEN we delete some entries with a certain locale
    result = runner.invoke(
        args=[
            'i18n',
            'delete',
            '--locale',
            'en-US',
            'alt.logo'])
    # THEN we expect the correct entry count in database
    assert db.session.query(I18NValue).count() == 5
    # THEN we expect the deleted entry not to be in database
    assert not db.session.query(I18NValue).filter_by(
        key_id='alt.logo', locale_code='en-US').first()
    # WHEN we delete entries recursively with all locales
    result = runner.invoke(
        args=[
            'i18n',
            'delete',
            '-r',
            'app'])
    # THEN we expect the correct entry count in database
    assert db.session.query(I18NValue).count() == 1
    # THEN we expect the corresponding key to be deleted
    keys = db.session.query(I18NKey).all()
    assert len(keys) == 1
    assert keys[0].id == 'alt.logo'

    # WHEN we delete non-recursively without specifying a path
    result = runner.invoke(
        args=[
            'i18n',
            'delete',
            '--locale',
            'es-EC'
        ])
    # THEN we expect a warning message
    assert b'specify a PATH' in result.stdout_bytes

    # GIVEN one remaining entry with the 'es-EC' locale
    assert db.session.query(I18NValue).filter_by(
        locale_code="es-EC").count() == 1
    # WHEN we delete recursively without specifying a path
    result = runner.invoke(
        args=[
            'i18n',
            'delete',
            '-r',
            '--locale',
            'es-EC'
        ])
    # THEN we expect no values of the corresponding locale to exist
    assert db.session.query(I18NValue).filter_by(
        locale_code="es-EC").count() == 0
    # THEN we expect the key not to be deleted, because we specified a locale
    assert db.session.query(I18NKey).count() == 1


def test_i18n_translate(runner):
    # GIVEN a database with some entries
    locale_data = [{'code': 'en-US', 'desc': 'English US'}]
    key_data = [
        {'id': 'alt.logo', 'desc': 'Alt text for logo'},
        {'id': 'app.name', 'desc': 'Application name'},
        {'id': 'app.desc', 'desc': 'This is a test application'}
    ]
    populate_database_i18n(locale_data, key_data)
    # WHEN we translate the entries into Spanish
    result = runner.invoke(
        args=[
            'i18n',
            'translate',
            'en-US',
            'es-EC'])
    # THEN we expect the translated entries to appear in the database
    assert db.session.query(I18NValue).filter_by(
        locale_code="es-EC").count() == 3


def test_i18n_translate_params(runner):
    # GIVEN nothing
    # WHEN we invoke the command with an undeducible locale
    result = runner.invoke(
        args=[
            'i18n',
            'translate',
            'en-US',
            'ab-CD'])
    # THEN we expect the command to exit with status code 1
    assert result.exit_code == 1
    # THEN we expect the output to contain language code information
    assert b"indonesian" in result.stdout_bytes
    assert b"english" in result.stdout_bytes
    assert b"zh-cn" in result.stdout_bytes

import os

import click
from click import BadParameter
from flask.cli import AppGroup
from flask_jwt_extended import create_access_token

from flask import jsonify

#Needed for pruning events
from datetime import datetime, timedelta

from src import create_app
from src import db
from src.i18n.models import Language, I18NLocale
from src.people.models import Person, Account, Role
from src.people.test_people import create_multiple_people, create_multiple_accounts
from src.images.create_image_data import create_images_test_data
from src.events.models import Event
from src.events.create_event_data import create_events_test_data
from src.attributes.models import Attribute, PersonAttribute, EnumeratedValue
from src.attributes.test_attributes import create_multiple_attributes, create_multiple_enumerated_values, create_multiple_person_attribute_enumerated, create_multiple_person_attribute_strings
from src.people.test_people import create_multiple_people, create_multiple_accounts, create_multiple_managers, create_multiple_people_attributes
from src.places.test_places import create_multiple_areas, create_multiple_addresses, create_multiple_locations
from src.places.models import Country
from src.courses.models import Course, Course_Offering, Diploma
from src.courses.test_courses import create_multiple_courses, create_multiple_course_offerings,\
    create_multiple_diplomas, create_multiple_students, create_class_meetings,\
    create_diploma_awards, create_class_attendance, create_multiple_prerequisites, create_course_completion

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# ---- Data

data_cli = AppGroup('data', help="Manipulate application data.")


def _load_locales():
    locales = [
        I18NLocale(code='es-EC', desc='Español Ecuador'),
        I18NLocale(code='en-US', desc='English US')
    ]
    db.session.add_all(locales)
    db.session.commit()


@data_cli.command('load-locales', help="Load locales")
def load_locales():
    _load_locales()


@data_cli.command('load-countries', help='Load country codes')
def load_countries():
    Country.load_from_file()


@data_cli.command('load-languages', help='Load language codes')
def load_languages():
    Language.load_from_file()


@data_cli.command('load-roles', help='Load roles')
def load_roles():
    Role.load_from_file()

@data_cli.command('load-attribute-types', help='Load attribute types')
def load_attribute_types():
    Attribute.load_types_from_file()


@data_cli.command('load-all', help='Load everything')
def load_all():
    access_token = create_access_token(identity='test-user')
    _load_locales()
    Country.load_from_file()
    Language.load_from_file()
    Role.load_from_file()
    Attribute.load_types_from_file()
    create_multiple_people(db.session, 17)
    create_multiple_accounts(db.session, 0.25)
    access_token = create_access_token(identity='test-user')

    create_multiple_areas(db.session, 5)
    create_multiple_addresses(db.session, 10)
    create_multiple_locations(db.session, 20)


    create_images_test_data(db.session)

    create_multiple_people(db.session, 17)
    create_multiple_accounts(db.session, 0.25)
    create_multiple_courses(db.session, 12)
    create_multiple_course_offerings(db.session, 25)
    create_multiple_prerequisites(db.session)
    create_multiple_diplomas(db.session, 30)
    create_multiple_students(db.session, 60)
    create_class_meetings(db.session, 30)
    create_events_test_data(db.session)
    # create_diploma_awards(db.session, 30)
    # create_class_attendance(db.session, 30)
    create_diploma_awards(db.session, 30)
    create_class_attendance(db.session, 30)
    create_course_completion(db.session, 30)

    create_multiple_people_attributes(db.session, 5)
    create_multiple_managers(db.session, 2, 'Group Overseer')
    create_multiple_managers(db.session, 5, 'Group Leader', 'Group Overseer')


@data_cli.command('test', help='Load everything')
def test_random_data():
    from src.events.test_events import event_object_factory
    print(event_object_factory(db.session))


@data_cli.command('clear-all', help="Clear all data; drops and creates all tables")
def clear():
    db.drop_all()
    db.create_all()


app.cli.add_command(data_cli)

# ---- Users and Accounts

user_cli = AppGroup('account', help="Maintain account data.")


@user_cli.command('new', help="Create new account")
@click.argument('username')
@click.argument('password')
@click.option('--first', help="First name")
@click.option('--last', help="Last name")
def create_account(username, password, first, last):
    first_name = first or 'Test'
    last_name = last or 'User'

    # Make sure no existing user.
    person = db.session.query(Account).filter_by(username=username).first()
    if person is not None:
        raise BadParameter(f"Already an account with username '{username}'")

    # Create the Person; commit to DB so we get ID
    person = Person(first_name=first_name, last_name=last_name)
    account = Account(username=username, password=password, person=person)
    db.session.add(account)
    db.session.commit()
    print(f"Created {person}")
    print(f"Created {account}")


@user_cli.command('password', help="Set password")
@click.argument('username')
@click.argument('password')
def update_password(username, password):
    person = db.session.query(Account).filter_by(username=username).first()
    if person is None:
        raise BadParameter(f"No account with username '{username}'")

    person.password = password
    db.session.commit()
    print(f"Password for '{username}' updated")

app.cli.add_command(user_cli)


# ---- Courses and Relating to Courses

course_cli = AppGroup('course', help="Maintain course data.")


@course_cli.command('new', help="Create new course")
@click.argument('name')
@click.argument('description')
@click.option('--prereq', help="Number of prerequisites to make")
@click.option('--offering', help="Name of offering to make for course")
def create_course(name, description, prereq, offering):

    # Create the Course and Prereq Courses; commit to DB so we get ID
    course = Course(name=name, description=description)

    if prereq is not None:
        if str.isnumeric(prereq):
            for i in range(int(prereq)):
                course.prerequisites.append(Course(name=f"prereq course{i}",
                        description=f"here we are using the command line.{i}"))
        else:
            prereq_course = db.session.query(Course).filter_by(name=prereq).first()
            print(prereq_course)
            course.prerequisites.append(prereq_course)

    if offering is not None:
        course_offering = Course_Offering(course_id=course.id,
                        description=offering, max_size=2, active=True)
        course.courses_offered.append(course_offering)
    db.session.add(course)
    db.session.commit()
    print(f"Created {course}")
    print(f"Created Prerequisites {course.prerequisites}")
    print(f"Created Course Offering {course.courses_offered}")


app.cli.add_command(course_cli)


# ---- Diploma

diploma_cli = AppGroup('diploma', help="Maintain diploma data.")


@diploma_cli.command('new', help="Create new diploma")
@click.argument('name')
@click.argument('description')
def create_diploma(name, description):
    # Create the diploma; commit to DB so we get ID
    diploma = Diploma(name=name, description=description)
    db.session.add(diploma)
    db.session.commit()
    print(f"Created Diploma {diploma}")


app.cli.add_command(diploma_cli)

# ---- Maintainence

maintain_cli = AppGroup('maintain', help="Mantaining the database.")

@maintain_cli.command('prune-events', help="Sets events that have ended before <pruningOffset> to inactive")
def prune_events():
    events = db.session.query(Event).filter_by(active=True).all()
    pruningOffset = datetime.now() - timedelta(days=30)
    for event in events:
        if(event.end < pruningOffset):
            event.active = False
    db.session.commit()

app.cli.add_command(maintain_cli)

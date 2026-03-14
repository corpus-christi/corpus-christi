"""Typer CLI replacing Flask AppGroup commands."""
from datetime import datetime, timedelta

import typer

app = typer.Typer(help="Corpus Christi CLI")
app_cli = typer.Typer(help="Maintain application-wide data.")
people_cli = typer.Typer(help="Maintain accounts.")
courses_cli = typer.Typer(help="Maintain course data.")
events_cli = typer.Typer(help="Maintain events.")
faker_cli = typer.Typer(help="Load fake data for testing")

app.add_typer(app_cli, name="app")
app.add_typer(people_cli, name="people")
app.add_typer(courses_cli, name="courses")
app.add_typer(events_cli, name="events")
app.add_typer(faker_cli, name="faker")


def _get_db():
    from src.db import SessionLocal
    return SessionLocal()


def no_rows(db, model):
    from sqlalchemy import select, func
    count = db.execute(select(func.count()).select_from(model)).scalar()
    if count:
        typer.echo(f"{model.__name__} count is {count}; skipping")
    else:
        typer.echo(f"No {model.__name__}; loading")
    return count == 0


# ---- app commands

@app_cli.command("load-locales", help="Load locales")
def load_locales():
    from src.i18n.models import I18NLocale
    db = _get_db()
    if no_rows(db, I18NLocale):
        locales = [
            I18NLocale(code='es-EC', desc='Español Ecuador'),
            I18NLocale(code='en-US', desc='English US'),
        ]
        db.add_all(locales)
        db.commit()
    db.close()


@app_cli.command("load-countries", help="Load country codes")
def load_countries():
    from src.places.models import Country
    db = _get_db()
    if no_rows(db, Country):
        Country.load_from_file()
    db.close()


@app_cli.command("load-languages", help="Load language codes")
def load_languages():
    from src.i18n.models import Language
    db = _get_db()
    if no_rows(db, Language):
        Language.load_from_file()
    db.close()


@app_cli.command("load-roles", help="Load roles")
def load_roles():
    from src.people.models import Role
    db = _get_db()
    if no_rows(db, Role):
        Role.load_from_file()
    db.close()


@app_cli.command("load-attribute-types", help="Load attribute types")
def load_attribute_types():
    from src.attributes.models import Attribute
    db = _get_db()
    if no_rows(db, Attribute):
        Attribute.load_types_from_file()
    db.close()


@app_cli.command("clear-all", help="Clear ALL data - DANGEROUS")
def clear_all():
    from src.db import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ---- people commands

@people_cli.command("new", help="Create new person")
def create_account(
    username: str = typer.Argument(...),
    password: str = typer.Argument(...),
    first: str = typer.Option(None, help="First name"),
    last: str = typer.Option(None, help="Last name"),
):
    from sqlalchemy import select
    from src.people.models import Person
    db = _get_db()
    first_name = first or 'Test'
    last_name = last or 'User'
    existing = db.execute(select(Person).where(Person.username == username)).scalar_one_or_none()
    if existing is not None:
        typer.echo(f"Error: Already an account with username '{username}'", err=True)
        raise typer.Exit(1)
    person = Person(first_name=first_name, last_name=last_name, username=username, password=password)
    db.add(person)
    db.commit()
    typer.echo(f"Created {person}")
    db.close()


@people_cli.command("password", help="Change password")
def update_password(
    username: str = typer.Argument(...),
    password: str = typer.Argument(...),
):
    from sqlalchemy import select
    from src.people.models import Person
    db = _get_db()
    person = db.execute(select(Person).where(Person.username == username)).scalar_one_or_none()
    if person is None:
        typer.echo(f"Error: No account with username '{username}'", err=True)
        raise typer.Exit(1)
    person.password = password
    db.commit()
    typer.echo(f"Password for '{username}' updated")
    db.close()


# ---- courses commands

@courses_cli.command("create-course", help="Create new course")
def create_course(
    name: str = typer.Argument(...),
    description: str = typer.Argument(...),
    prereq: str = typer.Option(None, help="Name of prerequisite"),
    offering: str = typer.Option(None, help="Name of offering to make for course"),
):
    from sqlalchemy import select
    from src.courses.models import Course, Course_Offering
    db = _get_db()
    course = Course(name=name, description=description)
    if prereq is not None:
        prereq_course = db.execute(select(Course).where(Course.name == prereq)).scalar_one_or_none()
        if prereq_course:
            course.prerequisites.append(prereq_course)
    if offering is not None:
        course_offering = Course_Offering(description=offering, max_size=2, active=True)
        course.courses_offered.append(course_offering)
    db.add(course)
    db.commit()
    typer.echo(f"Created {course}")
    typer.echo(f"Created Prerequisites {course.prerequisites}")
    typer.echo(f"Created Course Offering {course.courses_offered}")
    db.close()


@courses_cli.command("create-diploma", help="Create new diploma")
def create_diploma(
    name: str = typer.Argument(...),
    description: str = typer.Argument(...),
):
    from src.courses.models import Diploma
    db = _get_db()
    diploma = Diploma(name=name, description=description)
    db.add(diploma)
    db.commit()
    typer.echo(f"Created Diploma {diploma}")
    db.close()


# ---- events commands

@events_cli.command("prune-events", help="Sets events that have ended before 30 days to inactive")
def prune_events():
    from sqlalchemy import select
    from src.events.models import Event
    db = _get_db()
    events = db.execute(select(Event).where(Event.active == True)).scalars().all()
    pruning_offset = datetime.now() - timedelta(days=30)
    for event in events:
        if event.end < pruning_offset:
            event.active = False
    db.commit()
    typer.echo("Events pruned.")
    db.close()


# ---- faker commands

@faker_cli.command("people", help="Fake people")
def fake_people():
    from src.db import SessionLocal
    from src.people.test_people import create_multiple_people, create_accounts_roles
    with SessionLocal() as db:
        create_multiple_people(db, 17)
        create_accounts_roles(db, 0.75)


@faker_cli.command("places", help="Fake places")
def fake_places():
    from src.db import SessionLocal
    from src.places.test_places import create_multiple_areas, create_multiple_addresses, create_multiple_locations
    with SessionLocal() as db:
        create_multiple_areas(db, 5)
        create_multiple_addresses(db, 10)
        create_multiple_locations(db, 20)


@faker_cli.command("courses", help="Fake courses")
def fake_courses():
    from src.db import SessionLocal
    from src.people.test_people import create_multiple_people
    from src.courses.test_courses import (
        create_multiple_courses, create_multiple_course_offerings,
        create_multiple_prerequisites, create_multiple_diplomas,
        create_multiple_students, create_class_meetings,
        create_diploma_awards, create_class_attendance, create_course_completion,
    )
    with SessionLocal() as db:
        create_multiple_people(db, 17)
        create_multiple_courses(db, 12)
        create_multiple_course_offerings(db, 25)
        create_multiple_prerequisites(db)
        create_multiple_diplomas(db, 30)
        create_multiple_students(db, 60)
        create_class_meetings(db, 30)
        create_diploma_awards(db, 30)
        create_class_attendance(db, 30)
        create_course_completion(db, 30)


@faker_cli.command("events", help="Fake events")
def fake_events():
    from src.db import SessionLocal
    from src.events.create_event_data import create_events_test_data
    with SessionLocal() as db:
        create_events_test_data(db)


@faker_cli.command("groups", help="Fake groups")
def fake_groups():
    from src.db import SessionLocal
    from src.people.test_people import create_multiple_managers
    from src.groups.create_group_data import create_group_test_data
    with SessionLocal() as db:
        create_multiple_managers(db, 2, 'Group Overseer')
        create_multiple_managers(db, 5, 'Group Leader')
        create_group_test_data(db)


@faker_cli.command("images", help="Fake images")
def fake_images():
    from src.db import SessionLocal
    from src.images.create_image_data import create_images_test_data
    with SessionLocal() as db:
        create_images_test_data(db)


if __name__ == "__main__":
    app()

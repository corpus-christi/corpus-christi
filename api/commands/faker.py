from flask.cli import AppGroup
from src import db
from src.courses.test_courses import create_multiple_courses, create_multiple_course_offerings, \
    create_multiple_diplomas, create_multiple_students, create_class_meetings, \
    create_diploma_awards, create_class_attendance, create_multiple_prerequisites, \
    create_course_completion
from src.events.create_event_data import create_events_test_data
from src.groups.create_group_data import create_group_test_data
from src.images.create_image_data import create_images_test_data
from src.people.test_people import create_multiple_people, create_person_roles
from src.places.test_places import create_multiple_areas, create_multiple_addresses, create_multiple_locations


def create_faker_cli(app):
    faker_cli = AppGroup('faker', help="Load fake data for testing")

    @faker_cli.command('people', help='Fake people')
    def fake_people():
        create_multiple_people(db.session, 17)
        create_person_roles(db.session, 0.75)

    @faker_cli.command("places", help="Fake places")
    def fake_places():
        create_multiple_areas(db.session, 5)
        create_multiple_addresses(db.session, 10)
        create_multiple_locations(db.session, 20)

    @faker_cli.command("courses", help="Fake courses")
    def fake_courses():
        create_multiple_people(db.session, 17)
        create_multiple_courses(db.session, 12)
        create_multiple_course_offerings(db.session, 25)
        create_multiple_prerequisites(db.session)
        create_multiple_diplomas(db.session, 30)
        create_multiple_students(db.session, 60)
        create_class_meetings(db.session, 30)
        create_diploma_awards(db.session, 30)
        create_class_attendance(db.session, 30)
        create_course_completion(db.session, 30)

    @faker_cli.command("events", help="Fake events")
    def fake_events():
        create_events_test_data(db.session)

    @faker_cli.command("groups", help="Fake groups")
    def fake_groups():
        create_group_test_data(db.session)

    @faker_cli.command("images", help="Fake images")
    def fake_images():
        # Always put this close to last (since it has dependencies in all of
        # the major modules)
        create_images_test_data(db.session)

    app.cli.add_command(faker_cli)

from datetime import datetime, timedelta, date

from flask.cli import AppGroup

from .. import db
from ..events.models import Event


def create_event_cli(app):
    event_cli = AppGroup('events', help="Maintain events.")

    @event_cli.command('test-factory', help='Test event factory')
    def test_random_data():
        from ..src.events.test_events import event_object_factory
        print(event_object_factory(db.session))

    @event_cli.command('event-demo', help='create seed data for event demo')
    def create_event_demo():
        # USAGE: after modifying content in this function,
        # run:
        #       flask data clear-all
        #       flask data load-countries
        #       flask data event-demo
        # And the database should be populated with the data desired

        # Country.load_from_file() # uncomment this line if database is empty
        from ..src.places.test_places import create_location_nested
        from ..src.events.create_event_data import create_team, create_event, create_event_person, \
            create_event_participant
        from ..src.people.test_people import create_person

        # CREATE STATIC LOCATION, id is returned
        # def create_location_nested(sqla, country_code='EC',
        # area_name='Azuay', city='Cuenca', address, address_name,
        # description):
        create_location_nested(
            db.session,
            address='Avenida Loja',
            address_name='Arco Church',
            description='campsite')
        create_location_nested(db.session, address='Avenida Loja',
                               address_name='Arco Church', description='room')
        tid1 = create_team(db.session, description='worship')
        print(f"worship team id: {tid1}")
        tid2 = create_team(db.session, description='another crew')
        print(f"crew team id: {tid2}")

        # CREATE STATIC EVENT, id is returned
        # def create_event(sqla, title, description, start, end, location_id =
        # None, active=True):
        e1 = create_event(
            db.session, title='event1', description='description', start=datetime(
                2019, 2, 21, 8, 0), end=datetime(
                2019, 2, 22, 16, 0))
        e2 = create_event(
            db.session, title='event2', description='description', start=datetime(
                2019, 2, 21, 8, 0), end=datetime(
                2019, 2, 22, 16, 0))
        e3 = create_event(
            db.session, title='event3', description='description', start=datetime(
                2019, 2, 21, 8, 0), end=datetime(
                2019, 2, 22, 16, 0))

        print(f"event_id: {e1}")
        print(f"event_id: {e2}")
        print(f"event_id: {e3}")

        # CREATE STATIC PERSON, id is returned
        # def create_person(sqla, first_name, last_name, gender, birthday,
        # phone, email, active=True, address_id=None):
        p1 = create_person(
            db.session,
            first_name='first',
            last_name='last',
            gender='M',
            birthday=date(
                1900,
                2,
                3),
            phone='12345678',
            email='xxx@mail.com')
        p2 = create_person(
            db.session,
            first_name='first',
            last_name='last',
            gender='M',
            birthday=date(
                1900,
                2,
                3),
            phone='12345678',
            email='xxx@mail.com')
        p3 = create_person(
            db.session,
            first_name='first',
            last_name='last',
            gender='M',
            birthday=date(
                1900,
                2,
                3),
            phone='12345678',
            email='xxx@mail.com')
        p4 = create_person(
            db.session,
            first_name='first',
            last_name='last',
            gender='M',
            birthday=date(
                1900,
                2,
                3),
            phone='12345678',
            email='xxx@mail.com')
        p5 = create_person(
            db.session,
            first_name='first',
            last_name='last',
            gender='M',
            birthday=date(
                1900,
                2,
                3),
            phone='12345678',
            email='xxx@mail.com')
        print(f"person_id: {p1}")
        print(f"person_id: {p2}")
        print(f"person_id: {p3}")
        print(f"person_id: {p4}")
        print(f"person_id: {p5}")

        # CREATE STATIC EVENT PERSON, payload is returned
        # def create_event_person(sqla, event_id, person_id, description):
        ep = create_event_person(db.session, event_id=e1,
                                 person_id=p1, description="devotional leader")
        print(ep)
        ep = create_event_person(db.session, event_id=e2,
                                 person_id=p1, description="main speaker")
        print(ep)

        # CREATE STATIC EVENT PARTICIPANT, payload is returned
        # def create_event_participant(sqla, event_id, person_id,
        # confirmed=True):
        ep = create_event_participant(
            db.session, event_id=e1, person_id=p2, confirmed=True)
        print(ep)
        ep = create_event_participant(
            db.session, event_id=e2, person_id=p3, confirmed=True)
        print(ep)
        ep = create_event_participant(
            db.session, event_id=e1, person_id=p4, confirmed=True)
        print(ep)
        ep = create_event_participant(
            db.session, event_id=e2, person_id=p5, confirmed=True)
        print(ep)
        ep = create_event_participant(
            db.session, event_id=e1, person_id=p5, confirmed=True)
        print(ep)
        ep = create_event_participant(
            db.session, event_id=e1, person_id=p3, confirmed=True)
        print(ep)

    @event_cli.command(
        'prune-events',
        help="Sets events that have ended before <pruningOffset> to inactive")
    def prune_events():
        events = db.session.query(Event).filter_by(active=True).all()
        pruningOffset = datetime.now() - timedelta(days=30)
        for event in events:
            if (event.end < pruningOffset):
                event.active = False
        db.session.commit()

    app.cli.add_command(event_cli)

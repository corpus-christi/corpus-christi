import random
import datetime

import pytest
from faker import Factory
from faker.providers import lorem
from faker.providers import date_time
from flask import url_for

from .models import Event, EventSchema


fake = Factory.create();
fake.add_provider(lorem)
fake.add_provider(date_time)

def flip():
    return random.choice((True, False))


def get_date_range(start):
    start_hour = random.randint(0, 23)
    start_date_time = datetime.datetime(start.year, start.month, start.day, start_hour)
    end_hour = random.randint(start_hour, 23)
    end_date_time = datetime.datetime(start.year, start.month, start.day, end_hour)
    return str(start_date_time), str(end_date_time)


# Builds a fake event.
def event_object_factory():
    event = {
        'title': fake.word()
    }

    start = fake.date_between('now', '+1y')

    event['start'], event['end'] = get_date_range(start)

    return event


def create_multiple_events(sqla, n):
    event_schema = EventSchema()
    new_events = []
    for i in range(n):
        valid_event = event_schema.load(event_object_factory())
        new_events.append(Event(**valid_event))
    sqla.add_all(new_events)
    sqla.commit()


# ---- Event

@pytest.mark.smoke
def test_create_event(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    
    # WHEN
    for i in range(count):
        resp = auth_client.post(url_for('events.create_event'), json=event_object_factory())
        assert resp.status_code == 201
    
    # THEN
    assert auth_client.sqla.query(Event).count() == count
    

@pytest.mark.smoke
def test_read_all_events(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN
    resp = auth_client.get(url_for('events.read_all_events'))
    assert resp.status_code == 200
    events = auth_client.sqla.query(Event).all()

    # THEN
    assert len(events) == count
    assert len(resp.json) == count

    for i in range(count):
        assert resp.json[i]['title'] == events[i].title
    

@pytest.mark.smoke
def test_read_one_event(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)
    
    # WHEN
    events = auth_client.sqla.query(Event).all()
    
    # THEN
    assert len(events) == count

    for event in events:
        resp = auth_client.get(url_for('events.read_one_event', event_id = event.id))

        assert resp.status_code == 200
        assert resp.json['title'] == event.title
        # Datetimes come back in a slightly different format, but information is the same.
        # assert resp.json['start'] == str(event.start)
    

@pytest.mark.xfail()
def test_replace_event(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_event(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_event(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

# ---- Asset


@pytest.mark.xfail()
def test_create_asset(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_all_assets(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_one_asset(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_replace_asset(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_asset(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_asset(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

# ---- Team


@pytest.mark.xfail()
def test_create_team(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_all_teams(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_one_team(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_replace_team(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_team(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_team(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

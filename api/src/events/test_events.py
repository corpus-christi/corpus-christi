import pytest
import random
import datetime
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema, Event, EventSchema, Team, TeamSchema, EventParticipant, EventParticipantSchema, EventPerson, EventPersonSchema, TeamMember, TeamMemberSchema, EventAsset, EventAssetSchema, EventTeam, EventTeamSchema
from ..places.models import Location
from ..people.models import Person
from .create_event_data import create_multiple_events, event_object_factory

# ---- Event

@pytest.mark.smoke
def test_create_event(auth_client):
    # GIVEN an empty database
    # WHEN we add in some events
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

    for event in events:
        resp = auth_client.get(url_for('events.read_one_event'), event_id = event.id)
        assert resp.status_code == 200
        assert resp.json['title'] == event.title
        # Datetimes come back in a slightly different format, but information is the same.
        # assert resp.json['start'] == str(event.start)


@pytest.mark.xfail()
def test_replace_event(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_event(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_event(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

# ---- Asset


@pytest.mark.xfail()
def test_create_asset(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_all_assets(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_one_asset(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_replace_asset(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_asset(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_asset(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

# ---- Team


@pytest.mark.xfail()
def test_create_team(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_all_teams(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_one_team(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_replace_team(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_team(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_team(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    


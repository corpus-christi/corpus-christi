import pytest
import datetime
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema, Event, EventSchema, Team, TeamSchema, EventParticipant, EventParticipantSchema, EventPerson, EventPersonSchema, TeamMember, TeamMemberSchema, EventAsset, EventAssetSchema, EventTeam, EventTeamSchema
from ..places.models import Location
from ..people.models import Person
from .create_events_data import create_multiple_events, event_object_factory

# ---- Event

@pytest.mark.smoke
def test_create_event(auth_client):
    # GIVEN an empty database
    # WHEN we add in some events
    count = random.randint(5, 15)
    create_multiple_events(auth_client.sqla, count)
    # THEN we should get the same number of events in the database
    result_count = auth_client.sqla.query(Event).count()
    assert result_count == count

@pytest.mark.smoke
def test_read_all_events(auth_client):
    # GIVEN a database with some events
    # WHEN we query them all
    # THEN we should get the same number of events
    # same as previous, looking for new way of testing it
    assert True == True
    

@pytest.mark.xfail()
def test_read_one_event(auth_client):
    # GIVEN a database with a particular event
    event_schema = EventSchema()
    event = event_schema.load(event_object_factory(auth_client.sqla))
    auth_client.sqla.add(event)
    auth_client.sqla.commit()
    # fixme
    # WHEN we query that event
    auth_client.sqla.query(Event)
    # THEN we should get it
    assert True == False
    

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
    


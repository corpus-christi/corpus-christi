import math
import random

import pytest
import datetime
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema, Event, EventSchema, Team, TeamSchema

from .models import EventAsset, EventAssetSchema, EventTeam, EventTeamSchema


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()  # Generic faker; random-locale ones don't implement everything.


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def event_object_factory(sqla):
    """Cook up a fake event."""
    event = {
        'title': rl_fake().word(),
        'start': str(rl_fake().future_datetime(end_date="+6h")),
        'end': str(rl_fake().date_time_between(start_date="+6h", end_date="+1d", tzinfo=None)),
        'active': flip()
    }

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        event['description'] = rl_fake().sentences(nb=1)[0]
    #if flip():
        #event['location_id'] = random()%len(sqla.query(Location).all())
    return event


def asset_object_factory(sqla):
    """Cook up a fake asset."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    asset = {
        'description': rl_fake().sentences(nb=1)[0],
        #'location_id': random()%len(sqla.query(Location).all()),
        'active': flip()
    }
    return asset


def team_object_factory():
    """Cook up a fake asset."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    team = {
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip()
    }
    return team

def event_asset_object_factory(event_id, asset_id):
    """Cook up a fake eventasset json object from given ids."""
    eventasset = {
        'event_id': event_id,
        'asset_id': asset_id
    }
    return eventasset

def event_team_object_factory(event_id, team_id):
    """Cook up a fake eventteam json object from given ids."""
    eventteam = {
        'event_id': event_id,
        'team_id': team_id
    }
    return eventteam

def create_multiple_events(sqla, n):
    """Commit `n` new events to the database. Return their IDs."""
    event_schema = EventSchema()
    new_events = []
    for i in range(n):
        valid_events = event_schema.load(event_object_factory(sqla))
        new_events.append(Event(**valid_events))
    sqla.add_all(new_events)
    sqla.commit()

def create_multiple_teams(sqla, n):
    """Commit `n` new teams to the database. Return their IDs."""
    team_schema = TeamSchema()
    new_teams = []
    for i in range(n):
        valid_teams = team_schema.load(team_object_factory())
        new_teams.append(Team(**valid_teams))
    sqla.add_all(new_teams)
    sqla.commit()

def create_multiple_assets(sqla, n):
    """Commit `n` new assets to the database. Return their IDs."""
    asset_schema = AssetSchema()
    new_assets = []
    for i in range(n):
        valid_assets = asset_schema.load(asset_object_factory(sqla))
        new_assets.append(Asset(**valid_assets))
    sqla.add_all(new_assets)
    sqla.commit()

def create_events_assets(sqla, fraction=0.75):
    """Create data in the linking table between events and assets """
    event_asset_schema = EventAssetSchema()
    new_events_assets = []
    all_events_assets = sqla.query(Event, Asset).all()
    sample_events_assets = random.sample(all_events_assets, math.floor(len(all_events_assets) * fraction))
    #print(sample_events_assets[0][0].id)
    for events_assets in sample_events_assets:
        valid_events_assets = event_asset_schema.load(event_asset_object_factory(events_assets[0].id,events_assets[1].id))
        #print(valid_events_assets)
        new_events_assets.append(EventAsset(**valid_events_assets))
    #print(new_events_assets)
    sqla.add_all(new_events_assets)
    sqla.commit()


def create_events_teams(sqla, fraction=0.75):
    """Create data in the linking table between events and teams """
    event_team_schema = EventTeamSchema()
    new_events_teams = []
    all_events_teams = sqla.query(Event, Team).all()
    sample_events_teams = random.sample(all_events_teams, math.floor(len(all_events_teams) * fraction))
    #print(sample_events_teams[0][0].id)
    for events_teams in sample_events_teams:
        #print(events_teams)
        valid_events_teams = event_team_schema.load(event_team_object_factory(events_teams[0].id,events_teams[1].id))
        #print(valid_events_teams)
        new_events_teams.append(EventTeam(**valid_events_teams))
    #print(new_events_teams)
    sqla.add_all(new_events_teams)
    sqla.commit()


def create_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_events(sqla, 10)
    create_multiple_assets(sqla, 10)
    create_multiple_teams(sqla, 10)
    create_events_assets(sqla, 10)


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
    


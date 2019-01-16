import math
import random

import pytest
import datetime
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema, Event, EventSchema, Team, TeamSchema, EventParticipant, EventParticipantSchema, EventPerson, EventPersonSchema, TeamMember, TeamMemberSchema
from ..places.models import Location
from ..people.models import Person

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
    if flip():
        all_locations = sqla.query(Location).all()
        if len(all_locations) > 0:
            event['location_id'] = all_locations[random.randint(0, len(all_locations)-1)].id
    return event


def asset_object_factory(sqla):
    """Cook up a fake asset."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    all_locations = sqla.query(Location).all()
    asset = {
        'description': rl_fake().sentences(nb=1)[0],
        'location_id': all_locations[random.randint(0, len(all_locations)-1)].id,
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

def event_participant_object_factory(event_id, person_id):
    """Cook up a fake eventteam json object from given ids."""
    eventparticipant = {
        'event_id': event_id,
        'person_id': person_id,
        'confirmed': flip()
    }
    return eventparticipant

def event_person_object_factory(event_id, person_id):
    """Cook up a fake eventteam json object from given ids."""
    eventperson = {
        'event_id': event_id,
        'person_id': person_id,
        'description': rl_fake().sentences(nb=1)[0],
    }
    return eventperson

def team_member_object_factory(team_id, member_id):
    """Cook up a fake eventteam json object from given ids."""
    teammember = {
        'team_id': team_id,
        'member_id': member_id
    }
    return teammember

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

def create_events_participants(sqla, fraction=0.75):
    """Create data in the linking table between events and participants """
    event_participant_schema = EventParticipantSchema()
    new_events_participants = []
    all_events_participants = sqla.query(Event, Person).all()
    sample_events_participants = random.sample(all_events_participants, math.floor(len(all_events_participants) * fraction))
    #print(sample_events_participants[0][0].id)
    for events_participants in sample_events_participants:
        #print(events_participants)
        valid_events_participants = event_participant_schema.load(event_participant_object_factory(events_participants[0].id,events_participants[1].id))
        #print(valid_events_participants)
        new_events_participants.append(EventParticipant(**valid_events_participants))
    #print(new_events_participants)
    sqla.add_all(new_events_participants)
    sqla.commit()

def create_events_persons(sqla, fraction=0.75):
    """Create data in the linking table between events and persons """
    event_person_schema = EventPersonSchema()
    new_events_persons = []
    all_events_persons = sqla.query(Event, Person).all()
    sample_events_persons = random.sample(all_events_persons, math.floor(len(all_events_persons) * fraction))
    #print(sample_events_persons[0][0].id)
    for events_persons in sample_events_persons:
        #print(events_persons)
        valid_events_persons = event_person_schema.load(event_person_object_factory(events_persons[0].id,events_persons[1].id))
        #print(valid_events_persons)
        new_events_persons.append(EventPerson(**valid_events_persons))
    #print(new_events_persons)
    sqla.add_all(new_events_persons)
    sqla.commit()

def create_teams_members(sqla, fraction=0.75):
    """Create data in the linking table between teams and members """
    team_member_schema = TeamMemberSchema()
    new_teams_members = []
    all_teams_members = sqla.query(Team, Person).all()
    sample_teams_members = random.sample(all_teams_members, math.floor(len(all_teams_members) * fraction))
    #print(sample_teams_members[0][0].id)
    for teams_members in sample_teams_members:
        #print(teams_members)
        valid_teams_members = team_member_schema.load(team_member_object_factory(teams_members[0].id,teams_members[1].id))
        #print(valid_teams_members)
        new_teams_members.append(TeamMember(**valid_teams_members))
    #print(new_teams_members)
    sqla.add_all(new_teams_members)
    sqla.commit()

def create_events_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_events(sqla, 18)
    create_multiple_assets(sqla, 12)
    create_multiple_teams(sqla, 13)
    create_events_assets(sqla, 0.75)
    create_events_teams(sqla, 0.75)
    create_events_participants(sqla, 0.75)
    create_events_persons(sqla, 0.75)
    create_teams_members(sqla, 0.75)
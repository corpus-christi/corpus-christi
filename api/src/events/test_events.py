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
        'start': str(datetime.datetime(2019, 1, 3, 0, 30)),#rl_fake().future_datetime(end_date="+6h"),
        'end': str(datetime.datetime(2019, 1, 3, 1, 0)),#rl_fake().future_datetime(end_date="+1d"),
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

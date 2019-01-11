import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .. import db

from .models import Location, Address, Area, Country, AreaSchema, LocationSchema, AddressSchema

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
    return random.choice(auth_client.sqla.query(Area).all())

def area_factory(auth_client):
    """Create a fake area."""
    countries = auth_client.sqla.query(Country).all()
    area = {
        #using last_name for testing purposes, will be area name
        'name': rl_fake().last_name(),
        'country_code': random.choice(countries).code
    }

    return area
    areas = auth_client.sqla.query(Area).all()

def address_factory(auth_client):
    """Create a fake address."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    addresslines = fake.address.splitlines
    current_area = random.choice(areas)

    address = {
        'name': fake.name(),
        'address': addresslines[0],
        'city': addresslines[1].split(",")[0],
        'area_id': current_area.id,
        'country_code': current_area.country_code,
        'latitude':random.random() * 360 - 180,
        'longitude': random.random() * 360 - 180
    }
    return address

def location_factory(auth_client):
    """Create a fake location"""
    fake = Faker()  # Use a generic one; others may not have all methods.
    addresses = auth_client.sqla.query(Address).all()
    current_address = random.choice(addresses)

    location = {
        'description': fake.name(),
        'address_id': current_location.address_id
    }
    return location

def create_multiple_areas(sqla, n, auth_client):
    """Commit `n` new areas to the database. Return their IDs."""
    area_schema = AreaSchema()
    new_areas = []
    for i in range(n):
        valid_area = area_schema.load(area_factory(auth_client))
        new_areas.append(Area(**valid_area))
    sqla.add_all(new_areas)
    sqla.commit()

def create_multiple_addresses(sqla, n, auth_client):
    """Commit `n` new addresses to the database. Return their IDs."""
    address_schema = AddressSchema()
    new_address = []
    for i in range(n):
        valid_address = address_schema.load(address_factory(auth_client))
        new_address.append(Area(**valid_address))
    sqla.add_all(new_address)
    sqla.commit()

def create_multiple_locations(sqla, n, auth_client):
    """Commit `n` new locations to the database. Return their IDs."""
    location_schema = LocationSchema()
    new_locations = []
    for i in range(n):
        valid_location = location_schema.load(location_factory(auth_client))
        new_locations.append(Area(**valid_location))
    sqla.add_all(new_locations)
    sqla.commit()

def prep_database(sqla):
    """Prepare the database with a random number of people, some of which have accounts.
    Returns list of IDs of the new accounts.
    """
    create_multiple_areas(sqla, random.randint(5, 15), auth_client)
    create_multiple_addresses(sqla, random.randint(5, 15), auth_client)
    create_multiple_locations(sqla, random.randint(5, 15), auth_client)
    return [area.id for area in sqla.query(Area.id).all()]


# ---- Area

@pytest.mark.smoke
def test_create_area(auth_client):
    # GIVEN an empty database
    Country.load_from_file()
    count = random.randint(5, 15)
    # WHEN we create a random number of new areas
    for i in range(count):
        resp = auth_client.post(url_for('places.create_area'), json=area_factory(auth_client))
        assert resp.status_code == 201
    # THEN we end up with the proper number of areas in the database
    assert auth_client.sqla.query(Area).count() == count

@pytest.mark.smoke
def test_read_area(auth_client):
    # GIVEN a DB with a collection areas.
    Country.load_from_file()
    count = random.randint(3, 11)
    create_multiple_areas(auth_client.sqla, count, auth_client)

    # WHEN we ask for them all
    areas = auth_client.sqla.query(Area).all()
    # THEN we exepct the same number
    assert db.session.query(Area).count() == count

    # WHEN we request each of them from the server
    for area in areas:
        resp = auth_client.get(url_for('places.read_one_area', area_id=area.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['name'] == area.name
        assert resp.json['country_code'] == area.country_code


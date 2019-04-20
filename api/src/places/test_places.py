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
from ..images.create_image_data import create_images_locations, create_test_images
from ..images.models import Image, ImageSchema, ImageLocation, ImageLocationSchema


area_schema = AreaSchema()
location_schema = LocationSchema()
address_schema = AddressSchema()

@pytest.mark.smoke
@pytest.mark.parametrize('code, name', [('US', 'United States'),
                                        ('EC', 'Ecuador'),
                                        ('TH', 'Thailand')])
def test_read_country(auth_client, code, name):
    count = Country.load_from_file()
    assert count > 0
    resp = auth_client.get(url_for('places.read_countries', country_code=code, locale='en-US'))
    assert resp.status_code == 200
    print("RESP", resp.json)
    assert resp.json['name'] == name


@pytest.mark.slow
def test_read_all_countries(auth_client):
    count = Country.load_from_file()
    assert count > 0
    resp = auth_client.get(url_for('places.read_countries', locale='en-US'))
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.smoke
def test_missing_locale(auth_client):
    resp = auth_client.get(url_for('places.read_countries'))
    assert resp.status_code == 400

    resp = auth_client.get(url_for('places.read_countries', country_code='US'))
    assert resp.status_code == 400

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

def area_factory(sqla):
    """Create a fake area."""
    countries = sqla.query(Country).all()
    if not countries:
        Country.load_from_file()
        countries = sqla.query(Country).all()
    area = {
        #using last_name for testing purposes, will be area name
        'name': rl_fake().last_name(),
        'country_code': random.choice(countries).code
    }

    return area
    areas = sqla.query(Area).all()

def address_factory(sqla):
    """Create a fake address."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    addresslines = fake.address().splitlines()
    areas = sqla.query(Area).all()
    if not areas:
        create_multiple_areas(sqla, random.randint(3, 6))
        areas = sqla.query(Area).all()
    current_area = random.choice(areas)

    address = {
        'name': fake.name(),
        'address': addresslines[0],
        'city': addresslines[1].split(",")[0],
        'area_id': current_area.id,
        'country_code': current_area.country_code,
        'latitude':random.random() * 0.064116 + -2.933783,
        'longitude': random.random() * 0.09952 + -79.055411
    }
    return address

def location_factory(sqla):
    """Create a fake location"""
    fake = Faker()  # Use a generic one; others may not have all methods.
    addresses = sqla.query(Address).all()
    if not addresses:
        create_multiple_addresses(sqla, random.randint(3, 6))
        addresses = sqla.query(Address).all()
    current_address = random.choice(addresses)

    location = {
        'description': fake.name(),
        'address_id': current_address.id
    }
    return location

def create_multiple_areas(sqla, n):
    """Commit `n` new areas to the database. Return their IDs."""
    area_schema = AreaSchema()
    new_areas = []
    for i in range(n):
        valid_area = area_schema.load(area_factory(sqla))
        new_areas.append(Area(**valid_area))
    sqla.add_all(new_areas)
    sqla.commit()

def create_multiple_addresses(sqla, n):
    """Commit `n` new addresses to the database. Return their IDs."""
    address_schema = AddressSchema()
    new_address = []
    for i in range(n):
        valid_address = address_schema.load(address_factory(sqla))
        new_address.append(Address(**valid_address))
    sqla.add_all(new_address)
    sqla.commit()

def create_multiple_locations(sqla, n):
    """Commit `n` new locations to the database. Return their IDs."""
    location_schema = LocationSchema()
    new_locations = []
    for i in range(n):
        valid_location = location_schema.load(location_factory(sqla))
        new_locations.append(Location(**valid_location))
    sqla.add_all(new_locations)
    sqla.commit()

# the addresses won't have latitude and longitude
def create_location_nested(sqla, address, address_name, description, country_code='EC', area_name='Azuay', city='Cuenca'):
    #{
    #------- Country related
    #        'country_code': 'US',                  # required for nesting
    #------- Area related
    #        'area_name': 'area name',              # required for nesting
    #------- Address related
    #        'city': 'Upland',                      # required if address doesn't exist in database
    #        'address': '236 W. Reade Ave.',        # required if address doesn't exist in database
    #        'address_name': 'Taylor University',   # required if address doesn't exist in database
    #------- Location related
    #        'description': 'Euler 217'             # optional
    #}
    # This method tries to link existing entries in Country, Area, Address table if possible, otherwise create
    # When there is at least a certain table related field in the payload, the foreign key specified in the payload for that table will be overridden by the fields given
    def debugPrint(msg):
        print(msg)
    resolving_keys = ('country_code', 'area_name', 'city', 'address', 'address_name')
    payload_data = locals()
    # process country information
    resolve_needed = True
    location_payload = {}

    if resolve_needed:
        debugPrint("starting to resolve")
        debugPrint(payload_data)
        # resolve country
        if 'country_code' not in payload_data:
            print("'country_code not specified in request body', 422")
            return 
        country = sqla.query(Country).filter_by(code=payload_data['country_code']).first()
        if not country:
            print(f"no country code found in database matching {payload_data['country_code']}")
            return 
        country_code = country.code
        debugPrint(f"Country code resolved: {country_code}")
        # resolve area
        if 'area_name' not in payload_data:
            print("'area_name not specified in request body', 422")
            return 
        area = sqla.query(Area).filter_by(country_code=country_code, name=payload_data['area_name']).first()
        area_id = None
        if area:
            area_id = area.id
            debugPrint(f"fetched existing area_id {area_id}")
        else:
            debugPrint(f"creating new area")
            area_payload = {
                    'name': payload_data['area_name'],
                    'country_code': country_code
            }
            valid_area = area_schema.load(area_payload)
            area = Area(**valid_area)
            sqla.add(area)
            sqla.flush()
            area_id = area.id
            debugPrint(f"new_area created with id {area_id}")
        # resolve address
        address_name_transform = {'address_name': 'name'}
        address_keys = ('city', 'address', 'address_name')
        address_payload = {k if k not in address_name_transform else address_name_transform[k]:v 
                for k, v in payload_data.items() if k in address_keys}
        address_payload['area_id'] = area_id
        address_payload['country_code'] = country_code
        address = sqla.query(Address).filter_by(**address_payload).first()
        address_id = None
        if address:
            address_id = address.id
            debugPrint(f"fetched existing address id {address_id}")
        else:
            debugPrint(f"creating new address")
            debugPrint(f"address payload {address_payload}")
            valid_address = address_schema.load(address_payload)
            address = Address(**valid_address)
            sqla.add(address)
            sqla.flush()
            address_id = address.id
            debugPrint(f"new_address created with id {address_id}")
        # setting the request for location with the address_id obtained
        location_payload['address_id'] = address_id
        location_payload['description'] = description
    else:
        debugPrint("no need to resolve")

    debugPrint(f"final request for location: {location_payload} ")
    valid_location = location_schema.load(location_payload)

    new_location = Location(**valid_location)
    sqla.add(new_location)
    sqla.commit()

def prep_database(sqla):
    """Prepare the database with a random number of people, some of which have accounts.
    Returns list of IDs of the new accounts.
    """
    create_multiple_areas(sqla, random.randint(5, 15))
    create_multiple_addresses(sqla, random.randint(5, 15))
    create_multiple_locations(sqla, random.randint(5, 15))
    return [area.id for area in sqla.query(Area.id).all()]


# ---- Area

@pytest.mark.smoke
def test_create_area(auth_client):
    # GIVEN an empty database
    Country.load_from_file()
    count = random.randint(3, 6)

    # GIVEN areas with good data
    for i in range(count):
        new_area = area_factory(auth_client.sqla)

        # WHEN areas are attempted to be created
        resp = auth_client.post(url_for('places.create_area'), json = new_area)

        # THEN expect creates to run OK
        assert resp.status_code == 201

    # THEN expect rows to be created
    assert auth_client.sqla.query(Area).count() == count


@pytest.mark.smoke
def test_create_area_invalid(auth_client):
    # GIVEN an empty database
    Country.load_from_file()
    count = random.randint(3, 6)

    # GIVEN new areas with bad data
    for i in range(count):
        new_area = area_factory(auth_client.sqla)
        if flip():
            new_area['name'] = None
        if flip():
            new_area['country_code'] = None
        if not (new_area['name'] is None or new_area['country_code'] is None):
            new_area[fake.word()] = fake.word()

        # WHEN areas with bad data are attempted to be created
        resp = auth_client.post(url_for('places.create_area'), json = new_area)

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422

    # THEN expect no rows to be created
    assert auth_client.sqla.query(Area).count() == 0


@pytest.mark.smoke
def test_read_area(auth_client):
    # GIVEN an empty DB
    # WHEN we add a collection of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    # WHEN we ask for them all
    areas = auth_client.sqla.query(Area).all()
    # THEN we expect the same number
    assert db.session.query(Area).count() == count

    # WHEN we request each of them from the server
    for area in areas:
        resp = auth_client.get(url_for('places.read_one_area', area_id=area.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['name'] == area.name
        assert resp.json['country_code'] == area.country_code


@pytest.mark.smoke
def test_read_all_areas(auth_client):
    # GIVEN an empty DB
    # WHEN we add a collection of areas.
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    assert count > 0
    
    # WHEN we request all areas from the server
    resp = auth_client.get(url_for('places.read_all_areas', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.smoke
def test_replace_area(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    areas = auth_client.sqla.query(Area).all()

    # GIVEN new areas with good data
    for area in areas:
        new_area = area_factory(auth_client.sqla)

        # WHEN areas are requested to be replaced with new areas
        resp = auth_client.put(url_for('places.replace_area', area_id = area.id), json = new_area)

        # THEN expect request to run OK
        assert resp.status_code == 200

        # THEN expect areas to be replaced
        assert resp.json['id'] == area.id
        if new_area['name'] != area.name:
            assert resp.json['name'] != area.name
        else:
            assert resp.json['name'] == area.name
        if new_area['country_code'] != area.country_code:
            assert resp.json['country_code'] != area.country_code
        else:
            assert resp.json['country_code'] == area.country_code


@pytest.mark.smoke
def test_replace_area_invalid(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    areas = auth_client.sqla.query(Area).all()

    # GIVEN new areas with bad data
    for area in areas:
        new_area = area_factory(auth_client.sqla)
        if flip():
            new_area['name'] = None
        if flip():
            new_area['country_code'] = None
        if not (new_area['name'] is None or new_area['country_code'] is None):
            new_area[fake.word()] = fake.word()

        # WHEN areas are requested to be replaced with bad areas
        resp = auth_client.put(url_for('places.replace_area', area_id = area.id), json = new_area)

        # THEN expect request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_area(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    areas = auth_client.sqla.query(Area).all()

    # GIVEN good modifcation data
    for area in areas:
        mod = {}
        new_area = area_factory(auth_client.sqla)
        flips = (flip(), flip())
        if flips[0]:
            mod['name'] = new_area['name']
        if flips[1]:
            mod['country_code'] = new_area['country_code']

        # WHEN areas are requested to be updated
        resp = auth_client.patch(url_for('places.update_area', area_id = area.id), json = mod)

        # THEN expect request run OK
        assert resp.status_code == 200

        # THEN expect rows to be updated
        assert resp.json['id'] == area.id
        if flips[0] and mod['name'] != area.name:
            assert resp.json['name'] != area.name
        else:
            assert resp.json['name'] == area.name
        if flips[1] and mod['country_code'] != area.country_code:
            assert resp.json['country_code'] != area.country_code
        else:
            assert resp.json['country_code'] == area.country_code


@pytest.mark.smoke
def test_update_area_invalid(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    areas = auth_client.sqla.query(Area).all()

    # GIVEN bad modification data
    for area in areas:
        mod = {}
        flips = (flip(), flip(), flip())
        if flips[0]:
            mod['name'] = None
        if flips[1]:
            mod['country_code'] = None
        if flips[2] or not (flips[0] or flips[1]):
            mod[fake.word()] = fake.word()

        # WHEN areas are requested to be updated with bad data
        resp = auth_client.patch(url_for('places.update_area', area_id = area.id), json = mod)

        # THEN expect request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_area(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    areas = auth_client.sqla.query(Area).all()

    # WHEN areas are deleted
    deleted = 0
    for area in areas:
        resp = auth_client.delete(url_for('places.delete_area', area_id = area.id))
        deleted += 1

        # THEN for each delete expect delete to run OK
        assert resp.status_code == 204

        # THEN expect the area to be deleted
        assert auth_client.sqla.query(Area).count() == count - deleted


@pytest.mark.smoke
def test_delete_area_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN an area is requested to be deleted
    resp = auth_client.delete(url_for('places.delete_area', area_id = random.randint(1, 8)))

    # THEN expect row not to be found
    assert resp.status_code == 404


# ---- Address

@pytest.mark.smoke
def test_create_address(auth_client):
    # GIVEN an empty database
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    
    # WHEN we create a random number of new addresses
    for i in range(count):
        resp = auth_client.post(url_for('places.create_address'), json=address_factory(db.session))
        assert resp.status_code == 201
    # THEN we end up with the proper number of addresses in the database
    assert auth_client.sqla.query(Address).count() == count

@pytest.mark.smoke
def test_create_address_invalid(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    
    # WHEN a random number of addresses with bad data are requested to be created
    for i in range(count):
        new_address = address_factory(auth_client.sqla)
        new_address[fake.word()] = fake.word()
        resp = auth_client.post(url_for('places.create_address'), json = new_address)
        
        # THEN expect the requests to be unprocessable
        assert resp.status_code == 422

    # THEN expect there to be no addresses created
    assert len(auth_client.sqla.query(Address).all()) == 0

@pytest.mark.smoke
def test_read_address(auth_client):
    # GIVEN a DB with a collection addresses.
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    # WHEN we ask for them all
    addresses = auth_client.sqla.query(Address).all()
    # THEN we exepct the same number
    assert db.session.query(Address).count() == count

    # WHEN we request each of them from the server
    for address in addresses:
        resp = auth_client.get(url_for('places.read_one_address', address_id=address.id))
        # THEN we find a matching address
        assert resp.status_code == 200
        assert resp.json['name'] == address.name
        assert resp.json['address'] == address.address
        assert resp.json['city'] == address.city
        assert resp.json['area_id'] == address.area_id
        assert resp.json['country_code'] == address.country_code
        assert resp.json['latitude'] == address.latitude
        assert resp.json['longitude'] == address.longitude


@pytest.mark.smoke
def test_read_all_addresses(auth_client):
    # GIVEN a DB with a collection of addresses.
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    # WHEN we request all addresses from the server
    resp = auth_client.get(url_for('places.read_all_addresses', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == count


def query_address_with_params(auth_client, query_dict):
    result = auth_client.sqla.query(Address)
    print(query_dict.keys())
    if 'name' in query_dict.keys():
        result = result.filter_by(name=query_dict['name'])

    if 'address' in query_dict.keys():
        result = result.filter_by(address=query_dict['address'])

    if 'city' in query_dict.keys():
        result = result.filter_by(city=query_dict['city'])

    if 'area_id' in query_dict.keys():
        result = result.filter_by(area_id=query_dict['area_id'])   

    if 'country_code' in query_dict.keys():
        result = result.filter_by(country_code=query_dict['country_code'])

    if 'lat_start' in query_dict.keys():
        result = result.filter(Address.latitude > query_dict['lat_start'])

    if 'lat_end' in query_dict.keys():
        result = result.filter(Address.latitude < query_dict['lat_end'])

    if 'lon_start' in query_dict.keys():
        result = result.filter(Address.longitude > query_dict['lon_start'])

    if 'lon_end' in query_dict.keys():
        result = result.filter(Address.longitude < query_dict['lon_end']) 
    print(result)
    result = result.all()

    return result

@pytest.mark.smoke
def test_read_all_addresses_with_query(auth_client):
    # GIVEN a DB with a collection of addresses.
    Country.load_from_file()
    count = random.randint(9, 18)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    for i in range(count):
        # WHEN queried for all addresses matching a flag
        query_string = dict()
        addresses = auth_client.sqla.query(Address).all()
        address = random.choice(addresses)

        if i % 9 == 0:
            query_string['name'] = address.name

        if i % 9 == 1:
            query_string['address'] = address.address

        if i % 9 == 2:
            query_string['city'] = address.city
        
        if i % 9 == 3:
            query_string['area_id'] = address.area_id
        
        if i % 9 == 4:
            query_string['country_code'] = address.country_code

        if i % 9 == 5:
            query_string['lat_start'] = address.latitude - 1

        if i % 9 == 6:
            query_string['lat_end'] = address.latitude + 1

        if i % 9 == 7:
            query_string['lon_start'] = address.longitude - 1
        
        if i % 9 == 8:
            query_string['lon_end'] = address.longitude + 1

        filtered_results = query_address_with_params(auth_client, query_string)

        # WHEN we request all addresses from the server
        resp = auth_client.get(url_for('places.read_all_addresses'), query_string=query_string)
        # THEN the count matches the number of entries in the database
        assert resp.status_code == 200
        assert len(filtered_results) == len(resp.json)


        # assert len(resp.json) == 1

        # for event in resp.json:
        #     if 'return_group' in query_string:
        #         if query_string['return_group'] == 'inactive':
        #             assert event['active'] == False
        #     else:
        #         assert event['active'] == True

        #     if 'start' in query_string:
        #         assert datetime.datetime.strptime(event['start'][:event['start'].index('T')], '%Y-%m-%d') >= datetime.datetime.strptime(query_string['start'], '%Y-%m-%d')
        #     if 'end' in query_string:
        #         assert datetime.datetime.strptime(event['end'][:event['end'].index('T')], '%Y-%m-%d') <= datetime.datetime.strptime(query_string['end'], '%Y-%m-%d')

        #     if 'title' in query_string:
        #         assert query_string['title'].lower() in event['title'].lower()

        #     if 'location_id' in query_string:
        #         assert event['location_id'] == query_string['location_id']

@pytest.mark.smoke
def test_replace_address(auth_client):
    # GIVEN a set of areas and addresses
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    addresses = auth_client.sqla.query(Address).all()

    # GIVEN replacement addresses
    for address in addresses:
        new_address = address_factory(auth_client.sqla)

        # WHEN replace requests is made with new addresses
        resp = auth_client.put(url_for('places.replace_address', address_id = address.id), json = new_address)

        # THEN expect the requests to run OK
        assert resp.status_code == 200
        
        # THEN expect address to be updated
        if not new_address['name'] == address.name:
            assert not resp.json['name'] == address.name
        else:
            assert resp.json['name'] == address.name
        if not new_address['address'] == address.address:
            assert not resp.json['address'] == address.address
        else:
            assert resp.json['address'] == address.address
        if not new_address['city'] == address.city:
            assert not resp.json['city'] == address.city
        else:
            assert resp.json['city'] == address.city
        if not new_address['area_id'] == address.area_id:
            assert not resp.json['area_id'] == address.area_id
        else:
            assert resp.json['area_id'] == address.area_id
        if not new_address['country_code'] == address.country_code:
            assert not resp.json['country_code'] == address.country_code
        else:
            assert resp.json['country_code'] == address.country_code
        if not new_address['latitude'] == address.latitude:
            assert not resp.json['latitude'] == address.latitude
        else:
            assert resp.json['latitude'] == address.latitude
        if not new_address['longitude'] == address.longitude:
            assert not resp.json['longitude'] == address.longitude
        else:
            assert resp.json['longitude'] == address.longitude


@pytest.mark.smoke
def test_replace_address_invalid(auth_client):
    # GIVEN a set of areas and addresses
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    addresses = auth_client.sqla.query(Address).all()

    # GIVEN replacement addresses with bad data
    for address in addresses:
        new_address = address_factory(auth_client.sqla)
        new_address[fake.word()] = fake.word()

        # WHEN replace requests is made with bad data
        resp = auth_client.put(url_for('places.replace_address', address_id = address.id), json = new_address)

        # THEN expect the requests to be unprocessable
        assert resp.status_code == 422
        

@pytest.mark.smoke
def test_update_address(auth_client):
    # GIVEN a set of areas and addresses
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    addresses = auth_client.sqla.query(Address).all()

    # GIVEN modification data
    for address in addresses:
        new_address = address_factory(auth_client.sqla)
        mod = {}
        flips = (flip(), flip(), flip(), flip(), flip(), flip(), flip())
        if flips[0]:
            mod['name'] = new_address['name']
        if flips[1]:
            mod['address'] = new_address['address']
        if flips[2]:
            mod['city'] = new_address['city']
        if flips[3]:
            mod['area_id'] = new_address['area_id']
        if flips[4]:
            mod['country_code'] = new_address['country_code']
        if flips[5]:
            mod['latitude'] = new_address['latitude']
        if flips[6]:
            mod['longitude'] = new_address['longitude']

        # WHEN an update request is made with the modification data
        resp = auth_client.patch(url_for('places.update_address', address_id = address.id), json = mod)

        # THEN expect the request to run OK
        assert resp.status_code == 200
        
        # THEN expect address to be updated
        if flips[0] and not mod['name'] == address.name:
            assert not resp.json['name'] == address.name
        else:
            assert resp.json['name'] == address.name
        if flips[1] and not mod['address'] == address.address:
            assert not resp.json['address'] == address.address
        else:
            assert resp.json['address'] == address.address
        if flips[2] and not mod['city'] == address.city:
            assert not resp.json['city'] == address.city
        else:
            assert resp.json['city'] == address.city
        if flips[3] and not mod['area_id'] == address.area_id:
            assert not resp.json['area_id'] == address.area_id
        else:
            assert resp.json['area_id'] == address.area_id
        if flips[4] and not mod['country_code'] == address.country_code:
            assert not resp.json['country_code'] == address.country_code
        else:
            assert resp.json['country_code'] == address.country_code
        if flips[5] and not mod['latitude'] == address.latitude:
            assert not resp.json['latitude'] == address.latitude
        else:
            assert resp.json['latitude'] == address.latitude
        if flips[6] and not mod['longitude'] == address.longitude:
            assert not resp.json['longitude'] == address.longitude
        else:
            assert resp.json['longitude'] == address.longitude


@pytest.mark.smoke
def test_update_address_invalid(auth_client):
    # GIVEN a set of areas
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)

    # GIVEN modification data with bad data
    new_address = address_factory(auth_client.sqla)
    mod = {}
    flips = (flip(), flip(), flip(), flip(), flip(), flip(), flip())
    if flips[0]:
        mod['name'] = new_address['name']
    if flips[1]:
        mod['address'] = new_address['address']
    if flips[2]:
        mod['city'] = new_address['city']
    if flips[3]:
        mod['area_id'] = new_address['area_id']
    if flips[4]:
        mod['country_code'] = new_address['country_code']
    if flips[5]:
        mod['latitude'] = new_address['latitude']
    if flips[6]:
        mod['longitude'] = new_address['longitude']
    mod[fake.word()] = fake.word()

    # WHEN a request to update an address is made
    resp = auth_client.patch(url_for('places.update_address', address_id = random.randint(1,8)), json = mod)

    # THEN expect request to not be processable
    assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_address(auth_client):
    # GIVEN a set of areas and addresses
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    addresses = auth_client.sqla.query(Address).all()

    # WHEN addresses are deleted at random
    deleted = 0
    for address in addresses:
        if flip():
            resp = auth_client.delete(url_for('places.delete_address', address_id = address.id))
            deleted += 1

            # THEN expect each delete to run OK
            assert resp.status_code == 204

    # THEN expect the correct number of addresses were deleted
    addresses = auth_client.sqla.query(Address).all()
    assert len(addresses) == count - deleted


@pytest.mark.smoke
def test_delete_address_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN an address is requested to be deleted
    resp = auth_client.delete(url_for('places.delete_address', address_id = random.randint(1, 8)))
    
    # THEN expect row not to be found
    assert resp.status_code == 404


# ---- Location

@pytest.mark.smoke
def test_create_location(auth_client):
    # GIVEN an empty database
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    # WHEN we create a random number of new locations
    for i in range(count):
        resp = auth_client.post(url_for('places.create_location'), json=location_factory(db.session))
        assert resp.status_code == 201
    # THEN we end up with the proper number of locations in the database
    assert auth_client.sqla.query(Location).count() == count


@pytest.mark.smoke
def test_create_location_invalid(auth_client):
    # GIVEN a set of areas and addresses
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)

    # GIVEN new locations with bad data
    for i in range(count):
        new_location = location_factory(auth_client.sqla)
        new_location[fake.word()] = fake.word()
        
        # WHEN locations with bad data are requested to be created
        resp = auth_client.post(url_for('places.create_location'), json = new_location)
        
        # THEN expect requests to be unprocessable
        assert resp.status_code == 422

    # THEN expect no locations to be created
    assert auth_client.sqla.query(Location).count() == 0

@pytest.mark.smoke
def test_create_location_nested(auth_client):
    # GIVEN with some countries
    Country.load_from_file()
    # WHEN we send a request with nested information
    payload = {
            'country_code': 'US',
            'area_name': 'area name',
            'latitude': 0,
            'longitude': 0,
            'city': 'Upland',
            'address': '236 W. Reade Ave.',
            'address_name': 'Taylor University',
            'description': 'Euler 217'
    }
    resp = auth_client.post(url_for('places.create_location'), json = payload)
    # THEN we expect the correct status code
    assert resp.status_code == 201
    # WHEN we expect an area being created
    assert auth_client.sqla.query(Area).count() == 1
    # THEN we expect an address to be created
    assert auth_client.sqla.query(Address).count() == 1
    # THEN we expect a location to be created
    assert auth_client.sqla.query(Location).count() == 1

    # WHEN we send another request with existing area and addresses
    resp = auth_client.post(url_for('places.create_location'), json = payload)
    # THEN we expect the correct status code
    assert resp.status_code == 201
    # WHEN we expect no area being created
    assert auth_client.sqla.query(Area).count() == 1
    # THEN we expect no address to be created
    assert auth_client.sqla.query(Address).count() == 1
    # THEN we expect 2 locations in total in the database
    assert auth_client.sqla.query(Location).count() == 2

    # WHEN we send an incomplete request
    incomplete_payload = {
            'country_code': 'US',
            'latitude': 0,
            'longitude': 0,
            'city': 'Upland',
            'address': '236 W. Reade Ave.',
            'address_name': 'Taylor University',
            'description': 'Euler 217'
    }
    resp = auth_client.post(url_for('places.create_location'), json = incomplete_payload)
    # THEN we expect an error
    assert resp.status_code == 422





@pytest.mark.smoke
def test_read_all_locations(auth_client):
    # GIVEN a DB with a collection of addresses.
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)
    assert count > 0

    # WHEN we request all addresses from the server
    resp = auth_client.get(url_for('places.read_all_locations', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.smoke
def test_read_one_location(auth_client):
    # GIVEN a DB with a collection locations.
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    # WHEN we ask for them all
    locations = auth_client.sqla.query(Location).all()
    # THEN we exepct the same number
    assert db.session.query(Location).count() == count

    # WHEN we request each of them from the server
    for location in locations:
        resp = auth_client.get(url_for('places.read_one_location', location_id=location.id))
        # THEN we find a matching location
        assert resp.status_code == 200
        assert resp.json['description'] == location.description
        assert resp.json['address_id'] == location.address_id


@pytest.mark.smoke
def test_replace_location(auth_client):
    # GIVEN a set of areas, addresses, and locations
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    locations = auth_client.sqla.query(Location).all()
    
    # GIVEN replacement locations
    for location in locations:
        new_location = location_factory(auth_client.sqla)

        # WHEN locations are requested to be replaced
        resp = auth_client.put(url_for('places.replace_location', location_id = location.id), json = new_location)

        # THEN expect an OK response
        assert resp.status_code == 200

        # THEN expect locations to be replaced but with consistent ids
        assert resp.json['id'] == location.id

        if not location.description == new_location['description']:
            assert not resp.json['description'] == location.description
        else:
            assert resp.json['description'] == location.description

        if not location.address_id == new_location['address_id']:
            assert not resp.json['address_id'] == location.address_id
        else:
            assert resp.json['address_id'] == location.address_id


@pytest.mark.smoke
def test_replace_location_invalid(auth_client):
    # GIVEN a set of areas, addresses, and locations
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    locations = auth_client.sqla.query(Location).all()
    
    # Given replacement locations with bad data
    for location in locations:
        new_location = location_factory(auth_client.sqla)
        new_location[fake.word()] = fake.word()

        # WHEN locations are requested to be replaced
        resp = auth_client.put(url_for('places.replace_location', location_id = location.id), json = new_location)

        # THEN expect request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_location(auth_client):
    # GIVEN a set of areas, addresses, and locations
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    locations = auth_client.sqla.query(Location).all()
    
    # WHEN locations are deleted
    deleted = 0
    for location in locations:
        resp = auth_client.delete(url_for('places.delete_location', location_id = location.id))
        deleted += 1

        # THEN for each delete expect delete to run OK
        assert resp.status_code == 204

        # THEN expect the location to be deleted
        assert auth_client.sqla.query(Location).count() == count - deleted


@pytest.mark.smoke
def test_delete_location_no_exist(auth_client):
    # GIVEN an empty database
    
    # WHEN a location is requested to be deleted
    resp = auth_client.delete(url_for('places.delete_location', location_id = random.randint(1, 8)))
    
    # THEN expect row not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_update_location(auth_client):
    # GIVEN a set of areas, addresses, and locations
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    locations = auth_client.sqla.query(Location).all()
    
    # GIVEN modification data
    for location in locations:
        mod = {}
        flips = (flip(), flip())
        if flips[0]:
            mod['description'] = fake.sentences(nb=1)[0]
        if flips[1]:
            mod['address_id'] = random.randint(1, count + 1)

        # WHEN locations are updated with modification data
        resp = auth_client.patch(url_for('places.update_location', location_id = location.id), json = mod)

        # THEN expect an OK response
        assert resp.status_code == 200

        # THEN expect rows to be updated
        if flips[0] and not location.description == mod['description']:
            assert not resp.json['description'] == location.description
        else:
            assert resp.json['description'] == location.description

        if flips[1] and not location.address_id == mod['address_id']:
            assert not resp.json['address_id'] == location.address_id
        else:
            assert resp.json['address_id'] == location.address_id


@pytest.mark.smoke
def test_update_location_invalid(auth_client):
    # GIVEN a set of areas, addresses, and locations
    Country.load_from_file()
    count = random.randint(3, 6)
    create_multiple_areas(auth_client.sqla, count)
    create_multiple_addresses(auth_client.sqla, count)
    create_multiple_locations(auth_client.sqla, count)

    locations = auth_client.sqla.query(Location).all()
    
    # WHEN locations are updated with bad data
    for location in locations:
        resp = auth_client.patch(url_for('places.update_location', location_id = location.id), json = {fake.word(): fake.word()})

        #THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_location_no_exist(auth_client):
    # GIVEN no data in the database and some modification data
    mod = {}
    flips = (flip(), flip())
    if flips[0]:
        mod['description'] = fake.sentences(nb=1)[0]
    if flips[1]:
       mod['address_id'] = random.randint(1, 8)
        
    # WHEN update_location is called with mod data on a location
    resp = auth_client.patch(url_for('places.update_location', location_id = random.randint(1, 8)), json = mod)
    
    # THEN expect the location not to be found
    assert resp.status_code == 404


#   -----   __repr__


@pytest.mark.smoke
def test_repr_country(auth_client):
    country = Country()
    country.__repr__()


@pytest.mark.smoke
def test_repr_area(auth_client):
    area = Area()
    area.__repr__()


@pytest.mark.smoke
def test_repr_location(auth_client):
    location = Location()
    location.__repr__()


@pytest.mark.smoke
def test_repr_address(auth_client):
    address = Address()
    address.__repr__()


@pytest.mark.smoke
def test_add_location_images(auth_client):
    # GIVEN a set of locations and images
    count = random.randint(3, 6)
    create_multiple_locations(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    locations = auth_client.sqla.query(Location).all()
    images = auth_client.sqla.query(Image).all()
    
    # WHEN an image is requested to be tied to each location
    for i in range(count):
        print(i)
        resp = auth_client.post(url_for('places.add_location_images', location_id = locations[i].id, image_id = images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the location to have a single image
        assert len(auth_client.sqla.query(Location).filter_by(id = locations[i].id).first().images) == 1


@pytest.mark.smoke
def test_add_location_images_no_exist(auth_client):
    # GIVEN a set of locations and images
    count = random.randint(3, 6)
    create_multiple_locations(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    locations = auth_client.sqla.query(Location).all()
    images = auth_client.sqla.query(Image).all()
    
    # WHEN a no existant image is requested to be tied to an location
    resp = auth_client.post(url_for('places.add_location_images', location_id = 1, image_id = len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existant location
    resp = auth_client.post(url_for('places.add_location_images', location_id = count + 1, image_id = 1))

    # THEN expect the location not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_add_location_images_already_exist(auth_client):
    # GIVEN a set of locations, images, and location_image relationships
    count = random.randint(3, 6)
    create_multiple_locations(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_locations(auth_client.sqla)

    location_images = auth_client.sqla.query(ImageLocation).all()

    # WHEN existing location_image relationships are requested to be created
    for location_image in location_images:
        resp = auth_client.post(url_for('places.add_location_images', location_id = location_image.location_id, image_id = location_image.image_id))

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422



@pytest.mark.smoke
def test_delete_location_image(auth_client):
    # GIVEN a set of locations, images, and location_image relationships
    count = random.randint(3, 6)
    create_multiple_locations(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_locations(auth_client.sqla)

    valid_location_image = auth_client.sqla.query(ImageLocation).first()

    # WHEN the location_image relationships are requested to be deleted
    resp = auth_client.delete(url_for('places.delete_location_image', location_id = valid_location_image.location_id, image_id = valid_location_image.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204


@pytest.mark.smoke
def test_delete_location_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN an location_image relationship is requested to be deleted
    resp = auth_client.delete(url_for('places.delete_location_image', location_id = random.randint(1, 8), image_id = random.randint(1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404



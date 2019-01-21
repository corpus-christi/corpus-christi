import pytest
import random
import datetime
import random
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema
from ..places.models import Location, Country
from ..events.create_event_data import flip, fake, create_multiple_events, event_object_factory, email_object_factory, create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, create_events_persons, create_events_participants, create_teams_members, get_team_ids, asset_object_factory, team_object_factory
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas
from ..people.test_people import create_multiple_people

# ---- Asset

def generate_locations(auth_client):
    Country.load_from_file()
    create_multiple_areas(auth_client.sqla, 1)
    create_multiple_addresses(auth_client.sqla, 1)
    create_multiple_locations(auth_client.sqla, 2)


@pytest.mark.smoke
def test_create_asset(auth_client):
    # GIVEN a database with some locations
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    # WHEN we create an asset
    new_asset = {
            'description': fake.sentences(nb=1)[0],
            'active': flip(),
            'location_id': location_id
    }
    resp = auth_client.post(url_for('assets.create_asset'), json=new_asset)
    # THEN we expect the right status code
    assert resp.status_code == 201
    # THEN we expect the correct attributes of the given asset in the database
    queried_asset = auth_client.sqla.query(Asset).filter(Asset.id == resp.json["id"]).first()
    for attr in new_asset:
        assert new_asset[attr] == queried_asset.__dict__[attr]

@pytest.mark.smoke
def test_create_invalid_asset(auth_client):
    # GIVEN a database with some locations
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    # WHEN we create an asset
    new_asset = {
            'description': fake.sentences(nb=1)[0],
            'active': flip(),
            'location_id': location_id
    }

    if flip():
        new_asset['description'] = None
    elif flip():
        new_asset['active'] = None
    else:
        new_asset['location_id'] = None

    resp = auth_client.post(url_for('assets.create_asset'), json=new_asset)
    # THEN we expect the right status code
    assert resp.status_code == 422
    # THEN we expect the database to be unchanged
    assets = auth_client.sqla.query(Asset).all()
    assert len(assets) == 0


@pytest.mark.smoke
def test_read_all_assets(auth_client):
    generate_locations(auth_client)
    # GIVEN a database with a number of pre-defined assets
    assets = []
    count = random.randint(5, 15)
    for i in range(count):
        tmp_asset = asset_object_factory(auth_client.sqla)
        if i == 0:
            tmp_asset["description"] = "church drum"
            tmp_asset['active'] = True
        else:
            tmp_asset["description"] = "nothing to be filtered"
        assets.append(Asset(**AssetSchema().load(tmp_asset)))
    auth_client.sqla.add_all(assets)
    auth_client.sqla.commit()
    # WHEN we try to read all assets with a filter 'drum'
    filtered_assets = auth_client.get(url_for('assets.read_all_assets', return_group="all", desc="drum", sort='description_desc')).json
    # THEN we should have exactly one asset
    assert len(filtered_assets) == 1
    # GIVEN a database with some assets
    # WHEN we read all active ones
    active_assets = auth_client.get(url_for('assets.read_all_assets')).json
    queried_active_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==True).count()
    # THEN we should have the same amount as we do in the database
    assert len(active_assets) == queried_active_assets_count
    # THEN for each asset, the attributes should match
    for asset in active_assets:
        queried_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset["id"]).first()
        assert queried_asset.description == asset["description"]
        assert queried_asset.active == asset["active"]
    # WHEN we read all assets (active and inactive)
    all_assets = auth_client.get(url_for('assets.read_all_assets', return_group="all")).json
    # THEN we should have the same number
    assert len(all_assets) == count
    # WHEN we ask for all inactive assets
    inactive_assets = auth_client.get(url_for('assets.read_all_assets', return_group="inactive")).json
    queried_inactive_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==False).count()
    # THEN we should have the correct number of inactive assets
    assert len(inactive_assets) == queried_inactive_assets_count
    # WHEN we read all assets matching description
    all_assets_matching_desc = auth_client.get(url_for('assets.read_all_assets', desc='c')).json
    # THEN all results should match that description
    for asset in all_assets_matching_desc:
        assert 'c' in asset['description'].lower()
    all_assets_matching_loc_id = auth_client.get(url_for('assets.read_all_assets', location_id=1)).json
    # THEN all results should match that description
    for asset in all_assets_matching_loc_id:
        assert 1 == asset['location_id']
    

@pytest.mark.smoke
def test_read_one_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we read one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.get(url_for('assets.read_one_asset', asset_id = asset_id))
    # THEN we should have the correct status code
    assert resp.status_code == 200
    # THEN the asset should end up with the correct attribute
    asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
    assert resp.json["description"] == asset.description
    assert resp.json["active"] == asset.active
    # WHEN we try to read an asset that doesn't exist
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.get(url_for('assets.read_one_asset', asset_id = -99))
    # THEN we expect an error
    assert resp.status_code == 404
    


@pytest.mark.smoke
def test_read_one_missing_asset(auth_client):
    # GIVEN an empty database
    # WHEN we read one asset
    resp = auth_client.get(url_for('assets.read_one_asset', asset_id = 1))
    # THEN we should have the correct status code
    assert resp.status_code == 404

@pytest.mark.smoke
def test_replace_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we replace one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    location_id = auth_client.sqla.query(Location.id).first()[0]
    resp = auth_client.put(url_for('assets.update_asset', asset_id = asset_id), json={
        'description': dscrptn,
        'active': False,
        'location_id': location_id
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the asset should end up with the correct attribute
    new_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
    assert new_asset.description == dscrptn
    assert new_asset.active == False


@pytest.mark.smoke
def test_replace_invalid_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we replace one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    location_id = auth_client.sqla.query(Location.id).first()[0]
    json_request = {
        'description': dscrptn,
        'active': False,
        'location_id': location_id
    }
    if flip():
        json_request['description'] = None
    elif flip():
        json_request['active'] = None
    else:
        json_request['location_id'] = None
    resp = auth_client.put(url_for('assets.replace_asset', asset_id = asset_id), json=json_request)
    # THEN we should have the correct status code
    assert resp.status_code == 422
    

@pytest.mark.smoke
def test_update_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we update one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    location_id = auth_client.sqla.query(Location.id).first()[0]
    resp = auth_client.patch(url_for('assets.update_asset', asset_id = asset_id), json={
        'description': dscrptn,
        'active': False,
        'location_id': location_id
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the asset should end up with the correct attribute
    new_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
    assert new_asset.description == dscrptn
    assert new_asset.active == False


@pytest.mark.smoke
def test_update_invalid_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we update one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    location_id = auth_client.sqla.query(Location.id).first()[0]
    json_object = {
        'description': dscrptn,
        'active': False,
        'location_id': location_id
    }
    if flip():
        json_object['description'] = None
    elif flip():
        json_object['active'] = None
    else:
        json_object['location_id'] = None
    resp = auth_client.patch(url_for('assets.update_asset', asset_id = asset_id), json=json_object)
    # THEN we should have the correct status code
    assert resp.status_code == 422
    

@pytest.mark.smoke
def test_delete_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we delete one from it
    deleting_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.delete(url_for('assets.delete_asset', asset_id = deleting_id))
    # THEN we should have the correct status code
    assert resp.status_code == 204
    # THEN we should have the asset as inactive
    isActive = auth_client.sqla.query(Asset.active).filter(Asset.id == deleting_id).first()[0]
    assert isActive == False
    # WHEN we delete an asset that doesn't exist
    resp = auth_client.delete(url_for('assets.delete_asset', asset_id = 15000000))
    # THEN the response code should be accurate
    assert resp.status_code == 404
    
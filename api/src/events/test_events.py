import pytest
import random
import datetime
import random
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Asset, AssetSchema, Event, EventSchema, Team, TeamSchema, EventParticipant, EventParticipantSchema, EventPerson, EventPersonSchema, TeamMember, TeamMemberSchema, EventAsset, EventAssetSchema, EventTeam, EventTeamSchema
from ..places.models import Location, Country
from ..people.models import Person
from .create_event_data import create_multiple_events, event_object_factory, create_multiple_teams, flip
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas 

fake = Faker()

# ---- Event

@pytest.mark.smoke
def test_create_event(auth_client):
    # GIVEN an empty database
    # WHEN we add in some events
    count = random.randint(5, 15)
    
    # WHEN
    for i in range(count):
        resp = auth_client.post(url_for('events.create_event'), json=event_object_factory(auth_client.sqla))
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
    inactive = 0
    for event in events:
        if not event.active:
            inactive += 1

    assert len(events) == count
    assert len(resp.json) == count - inactive

    j = 0
    for i in range(count - inactive):
        if events[i].active:
            assert resp.json[j]['title'] == events[i].title
            j += 1


@pytest.mark.smoke
def test_read_one_event(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)
    
    # WHEN
    events = auth_client.sqla.query(Event).all()

    for event in events:
        # THEN
        resp = auth_client.get(url_for('events.read_one_event', event_id = event.id))
        assert resp.status_code == 200
        assert resp.json['title'] == event.title
        # Datetimes come back in a slightly different format, but information is the same.
        # assert resp.json['start'] == str(event.start)


@pytest.mark.smoke
def test_replace_event(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN
    events = auth_client.sqla.query(Event).all()

    for event in events:
        # THEN
        resp = auth_client.patch(url_for('events.replace_event', event_id = event.id), json = event_object_factory(auth_client.sqla))
        
        assert resp.status_code == 200
        assert resp.json['id'] == event.id
        assert resp.json['title'] != event.title
    

@pytest.mark.smoke
def test_update_event(auth_client):
    # GIVEN
    count = random.randint(3,11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN
    events = auth_client.sqla.query(Event).all()

    for event in events:
        # THEN
        payload = {}
        new_event = event_object_factory(auth_client.sqla)

        flips = (flip(), flip(), flip(), flip(), flip(), flip())

        print(new_event)
        if flips[0]:
            payload['title'] = new_event['title']
        if flips[1]:
            payload['start'] = new_event['start']
        if flips[2]:
            payload['end'] = new_event['end']
        if flips[3]:
            payload['active'] = new_event['active']
        if flips[4] and 'description' in new_event.keys():
            payload['description'] = new_event['description']
        if flips[5] and 'location_id' in new_event.keys():
            payload['location_id'] = new_event['location_id']

        resp = auth_client.patch(url_for('events.update_event', event_id = event.id), json=payload)

        assert resp.status_code == 200

        if flips[0]:
            assert resp.json['title'] == payload['title']
        if flips[1]:
            assert resp.json['start'] == payload['start'].replace(' ', 'T') + "+00:00"
        if flips[2]:
            assert resp.json['end'] == payload['end'].replace(' ', 'T') + "+00:00"
        if flips[3]:
            assert resp.json['active'] == payload['active']
        if flips[4] and 'description' in new_event.keys():
            assert resp.json['description'] == payload['description']
        if flips[5] and 'location_id' in new_event.keys():
            assert resp.json['location'] == payload['location_id']
    

@pytest.mark.smoke
def test_delete_event(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN
    events = auth_client.sqla.query(Event).all()

    deleted = 0
    for event in events:
        # THEN
        if flip():
            resp = auth_client.get(url_for('events.delete_event', event_id = event.id))
            assert resp.status_code == 200
            deleted += 1

    new_events = auth_client.sqla.query(Event).filter(Event.active == True).all()
    assert len(new_events) == count - deleted
    

# ---- Asset


#@pytest.mark.smoke
#def test_create_asset(auth_client):
#    # GIVEN a database with some locations
#    Country.load_from_file()
#    create_multiple_areas(auth_client.sqla, 1)
#    create_multiple_addresses(auth_client.sqla, 1)
#    create_multiple_locations(auth_client.sqla, 2)
#    location_id = auth_client.sqla.query(Location.id).first()[0]
#    print(location_id)
#
#    # WHEN we create an asset
#    new_asset = {
#            'description': fake.sentences(nb=1)[0],
#            'active': flip()
#    }
#    resp = auth_client.post(url_for('events.create_asset'), json=new_asset)
#    # THEN we expect the right status code
#    assert resp.status_code == 201
#    # THEN we expect the correct attributes of the given asset in the database
#    queried_asset = auth_client.sqla.query(Asset).filter(Asset.id == resp.json["id"]).first()
#    for attr in new_asset:
#        assert new_asset[attr] == queried_asset.__dict__[attr]
#    
#
#@pytest.mark.smoke
#def test_read_all_assets(auth_client):
#    # GIVEN a database with some assets
#    count = random.randint(5, 15)
#    create_multiple_assets(auth_client.sqla, count)
#    # WHEN we read all active ones
#    active_assets = auth_client.get(url_for('events.read_all_assets')).json
#    queried_active_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==True).count()
#    # THEN we should have the same amount as we do in the database
#    assert len(active_assets) == queried_active_assets_count
#    # THEN for each asset, the attributes should match
#    for asset in active_assets:
#        queried_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset["id"]).first()
#        assert queried_asset.description == asset["description"]
#        assert queried_asset.active == asset["active"]
#    # WHEN we read all assets (active and inactive)
#    all_assets = auth_client.get(url_for('events.read_all_assets', return_group="all")).json
#    # THEN we should have the same number
#    assert len(all_assets) == count
#    # WHEN we ask for all inactive assets
#    inactive_assets = auth_client.get(url_for('events.read_all_assets', return_group="inactive")).json
#    queried_inactive_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==False).count()
#    # THEN we should have the correct number of inactive assets
#    assert len(inactive_assets) == queried_inactive_assets_count
#    
#
#@pytest.mark.smoke
#def test_read_one_asset(auth_client):
#    # GIVEN a database with some assets
#    count = random.randint(5, 15)
#    create_multiple_assets(auth_client.sqla, count)
#    # WHEN we read one asset
#    asset_id = auth_client.sqla.query(Asset.id).first()[0]
#    resp = auth_client.get(url_for('events.read_one_asset', asset_id = asset_id))
#    # THEN we should have the correct status code
#    assert resp.status_code == 200
#    # THEN the asset should end up with the correct attribute
#    asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
#    assert resp.json["description"] == asset.description
#    assert resp.json["active"] == asset.active
#    
#
#@pytest.mark.smoke
#def test_replace_asset(auth_client):
#    # GIVEN a database with some assets
#    count = random.randint(5, 15)
#    create_multiple_assets(auth_client.sqla, count)
#    # WHEN we replace one asset
#    #new_asset = 
#    asset_id = auth_client.sqla.query(Asset.id).first()[0]
#    dscrptn = fake.sentences(nb=1)[0]
#    resp = auth_client.put(url_for('events.update_asset', asset_id = asset_id), json={
#        'description': dscrptn,
#        'active': False
#    })
#    # THEN we should have the correct status code
#    assert resp.status_code == 200 
#    # THEN the asset should end up with the correct attribute
#    new_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
#    assert new_asset.description == dscrptn
#    assert new_asset.active == False
#    
#
#@pytest.mark.smoke
#def test_update_asset(auth_client):
#    # GIVEN a database with some assets
#    count = random.randint(5, 15)
#    create_multiple_assets(auth_client.sqla, count)
#    # WHEN we update one asset
#    asset_id = auth_client.sqla.query(Asset.id).first()[0]
#    dscrptn = fake.sentences(nb=1)[0]
#    resp = auth_client.patch(url_for('events.update_asset', asset_id = asset_id), json={
#        'description': dscrptn,
#        'active': False
#    })
#    # THEN we should have the correct status code
#    assert resp.status_code == 200 
#    # THEN the asset should end up with the correct attribute
#    new_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
#    assert new_asset.description == dscrptn
#    assert new_asset.active == False
#    
#
#@pytest.mark.smoke
#def test_delete_asset(auth_client):
#    # GIVEN a database with some assets
#    count = random.randint(5, 15)
#    create_multiple_assets(auth_client.sqla, count)
#    # WHEN we delete one from it
#    deleting_id = auth_client.sqla.query(Asset.id).first()[0]
#    resp = auth_client.delete(url_for('events.delete_asset', asset_id = deleting_id))
#    # THEN we should have the correct status code
#    assert resp.status_code == 204
#    # THEN we should have the asset as inactive
#    isActive = auth_client.sqla.query(Asset.active).filter(Asset.id == deleting_id).first()[0]
#    assert isActive == False
    

# ---- Team


@pytest.mark.smoke
def test_create_team(auth_client):
    # GIVEN a database
    # WHEN we create a team
    new_team = {
            'description': fake.sentences(nb=1)[0],
            'active': flip()
    }
    resp = auth_client.post(url_for('events.create_team'), json=new_team)
    # THEN we expect the right status code
    assert resp.status_code == 201
    # THEN we expect the correct attributes of the given team in the database
    queried_team = auth_client.sqla.query(Team).filter(Team.id == resp.json["id"]).first()
    for attr in new_team:
        assert new_team[attr] == queried_team.__dict__[attr]
    

@pytest.mark.smoke
def test_read_all_teams(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we read all active ones
    active_teams = auth_client.get(url_for('events.read_all_teams')).json
    queried_active_teams_count = auth_client.sqla.query(Team).filter(Team.active==True).count()
    # THEN we should have the same amount as we do in the database
    assert len(active_teams) == queried_active_teams_count
    # THEN for each team, the attributes should match
    for team in active_teams:
        queried_team = auth_client.sqla.query(Team).filter(Team.id == team["id"]).first()
        assert queried_team.description == team["description"]
        assert queried_team.active == team["active"]
    # WHEN we read all teams (active and inactive)
    all_teams = auth_client.get(url_for('events.read_all_teams', return_group="all")).json
    # THEN we should have the same number
    assert len(all_teams) == count
    # WHEN we ask for all inactive teams
    inactive_teams = auth_client.get(url_for('events.read_all_teams', return_group="inactive")).json
    queried_inactive_teams_count = auth_client.sqla.query(Team).filter(Team.active==False).count()
    # THEN we should have the correct number of inactive teams
    assert len(inactive_teams) == queried_inactive_teams_count
    

@pytest.mark.smoke
def test_read_one_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we read one team
    team_id = auth_client.sqla.query(Team.id).first()[0]
    resp = auth_client.get(url_for('events.read_one_team', team_id = team_id))
    # THEN we should have the correct status code
    assert resp.status_code == 200
    # THEN the team should end up with the correct attribute
    team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert resp.json["description"] == team.description
    assert resp.json["active"] == team.active
    

@pytest.mark.smoke
def test_replace_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we replace one team
    #new_team = 
    team_id = auth_client.sqla.query(Team.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    resp = auth_client.put(url_for('events.update_team', team_id = team_id), json={
        'description': dscrptn,
        'active': False
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the team should end up with the correct attribute
    new_team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert new_team.description == dscrptn
    assert new_team.active == False
    

@pytest.mark.smoke
def test_update_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we update one team
    team_id = auth_client.sqla.query(Team.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    resp = auth_client.patch(url_for('events.update_team', team_id = team_id), json={
        'description': dscrptn,
        'active': False
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the team should end up with the correct attribute
    new_team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert new_team.description == dscrptn
    assert new_team.active == False
    

@pytest.mark.smoke
def test_delete_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we delete one from it
    deleting_id = auth_client.sqla.query(Team.id).first()[0]
    resp = auth_client.delete(url_for('events.delete_team', team_id = deleting_id))
    # THEN we should have the correct status code
    assert resp.status_code == 204
    # THEN we should have the team as inactive
    isActive = auth_client.sqla.query(Team.active).filter(Team.id == deleting_id).first()[0]
    assert isActive == False

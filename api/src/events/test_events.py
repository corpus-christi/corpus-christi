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
from .create_event_data import flip, fake, create_multiple_events, event_object_factory, create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, create_events_persons, create_events_participants, create_teams_members, get_team_ids, asset_object_factory
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas
from ..people.test_people import create_multiple_people

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
def test_create_invalid_event(auth_client):
    # GIVEN an empty database
    # WHEN we attempt to add invalid events
    count = random.randint(5, 15)

    for i in range(count):
        event = event_object_factory(auth_client.sqla)

        if flip():
            event['title'] = None
        elif flip():
            event['start'] = None
        else:
            event['end'] = None

        resp = auth_client.post(url_for('events.create_event'), json=event)
        
        # THEN the response should have the correct code
        assert resp.status_code == 422
    
    # AND the database should still be empty
    assert auth_client.sqla.query(Event).count() == 0

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
def test_read_all_events_with_query(auth_client):
    # GIVEN some existing events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)
    all_events = auth_client.sqla.query(Event).all()

    for _ in range(random.randint(10, 15)):
        # WHEN queried for all events matching a flag
        query_string = dict()
        if flip():
            query_string['return_group'] = 'inactive'
        elif flip():
            query_string['return_group'] = 'both'

        if flip():
            query_string['start'] = datetime.datetime.now().strftime('%Y-%m-%d')
        if flip():
            query_string['end'] = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if flip():
            query_string['title'] = 'c'
        
        if flip():
            query_string['location_id'] = 1

        if flip():
            query_string['include_assets'] = 1

        # THEN the response should match those flags
        resp = auth_client.get(url_for('events.read_all_events'), query_string=query_string)
        assert resp.status_code == 200
        events = auth_client.sqla.query(Event).all()

        for event in resp.json:
            if 'return_group' in query_string:
                if query_string['return_group'] == 'inactive':
                    assert event['active'] == False
            else:
                assert event['active'] == True

            if 'start' in query_string:
                assert datetime.datetime.strptime(event['start'][:event['start'].index('T')], '%Y-%m-%d') >= datetime.datetime.strptime(query_string['start'], '%Y-%m-%d')
            if 'end' in query_string:
                assert datetime.datetime.strptime(event['end'][:event['end'].index('T')], '%Y-%m-%d') <= datetime.datetime.strptime(query_string['end'], '%Y-%m-%d')

            if 'title' in query_string:
                assert query_string['title'].lower() in event['title'].lower()

            if 'location_id' in query_string:
                assert event['location_id'] == query_string['location_id']


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
def test_read_one_missing_event(auth_client):
    # GIVEN an empty database
    # WHEN a request for a specific event is made
    resp = auth_client.get(url_for('events.read_one_event', event_id=1))

    # THEN the response should have the appropriate error code
    assert resp.status_code == 404

@pytest.mark.smoke
def test_replace_event(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN
    events = auth_client.sqla.query(Event).all()

    for event in events:
        # THEN
        resp = auth_client.put(url_for('events.replace_event', event_id = event.id), json = event_object_factory(auth_client.sqla))
        
        assert resp.status_code == 200
        assert resp.json['id'] == event.id
        assert resp.json['title'] != event.title
    

@pytest.mark.smoke
def test_replace_invalid_event(auth_client):
    # GIVEN a database with events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we attempt to edit an invalid event
    original_event = auth_client.sqla.query(Event).first()
    modified_event = event_object_factory(auth_client.sqla)

    if flip():
        modified_event['title'] = None
    elif flip():
        modified_event['start'] = None
    else:
        modified_event['end'] = None

    resp = auth_client.put(url_for('events.replace_event', event_id=original_event.id), json=modified_event)
    
    # THEN the response should have the correct code
    assert resp.status_code == 422
    # AND the event should be unchanged
    new_event = auth_client.sqla.query(Event).filter(Event.id == original_event.id).first()
    assert new_event.title == original_event.title
    assert new_event.start == original_event.start
    assert new_event.end == original_event.end

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
def test_update_invalid_event(auth_client):
    # GIVEN a database with events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we attempt to edit an invalid event
    original_event = auth_client.sqla.query(Event).first()
    modified_event = event_object_factory(auth_client.sqla)

    if flip():
        modified_event['title'] = None
    elif flip():
        modified_event['start'] = None
    else:
        modified_event['end'] = None

    resp = auth_client.patch(url_for('events.update_event', event_id=original_event.id), json=modified_event)
    
    # THEN the response should have the correct code
    assert resp.status_code == 422
    # AND the event should be unchanged
    new_event = auth_client.sqla.query(Event).filter(Event.id == original_event.id).first()
    assert new_event.title == original_event.title
    assert new_event.start == original_event.start
    assert new_event.end == original_event.end

@pytest.mark.smoke
def test_update_missing_event(auth_client):
    # GIVEN an empty database
    # WHEN we attempt to edit an event
    event = event_object_factory(auth_client.sqla)
    resp = auth_client.patch(url_for('events.update_event', event_id=1), json=event)

    # THEN the response code should be correct
    assert resp.status_code == 404

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
        if flip() and event.active:
            resp = auth_client.delete(url_for('events.delete_event', event_id = event.id))
            assert resp.status_code == 204
            deleted += 1
        elif not event.active:
            deleted += 1

    new_events = auth_client.sqla.query(Event).filter(Event.active == True).all()
    assert len(new_events) == count - deleted
    

@pytest.mark.smoke
def test_delete_invalid_event(auth_client):
    # GIVEN an empty database
    # WHEN a delete request is sent
    resp = auth_client.delete(url_for('events.delete_event', event_id = 1))

    # THEN the response code should be correct
    assert resp.status_code == 404
    # AND the database should still be empty
    new_events = auth_client.sqla.query(Event).filter(Event.active == True).all()
    assert len(new_events) == 0

# ---- Asset

# ---- Asset-related helper functions
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
    resp = auth_client.post(url_for('events.create_asset'), json=new_asset)
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

    resp = auth_client.post(url_for('events.create_asset'), json=new_asset)
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
        else:
            tmp_asset["description"] = "nothing to be filtered"
        assets.append(Asset(**AssetSchema().load(tmp_asset)))
    auth_client.sqla.add_all(assets)
    auth_client.sqla.commit()
    print(auth_client.sqla.query(Asset).filter(Asset.description.like('%drum%')).all())
    # WHEN we try to read all assets with a filter 'drum'
    filtered_assets = auth_client.get(url_for('events.read_all_assets', desc="drum")).json
    # THEN we should have exactly one asset
    assert len(filtered_assets) == 1
    # GIVEN a database with some assets
    # WHEN we read all active ones
    active_assets = auth_client.get(url_for('events.read_all_assets')).json
    queried_active_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==True).count()
    # THEN we should have the same amount as we do in the database
    assert len(active_assets) == queried_active_assets_count
    # THEN for each asset, the attributes should match
    for asset in active_assets:
        queried_asset = auth_client.sqla.query(Asset).filter(Asset.id == asset["id"]).first()
        assert queried_asset.description == asset["description"]
        assert queried_asset.active == asset["active"]
    # WHEN we read all assets (active and inactive)
    all_assets = auth_client.get(url_for('events.read_all_assets', return_group="all")).json
    # THEN we should have the same number
    assert len(all_assets) == count
    # WHEN we ask for all inactive assets
    inactive_assets = auth_client.get(url_for('events.read_all_assets', return_group="inactive")).json
    queried_inactive_assets_count = auth_client.sqla.query(Asset).filter(Asset.active==False).count()
    # THEN we should have the correct number of inactive assets
    assert len(inactive_assets) == queried_inactive_assets_count
    # WHEN we read all assets matching description
    all_assets_matching_desc = auth_client.get(url_for('events.read_all_assets', desc='c')).json
    # THEN all results should match that description
    for asset in all_assets_matching_desc:
        assert 'c' in asset['description'].lower()
    

@pytest.mark.smoke
def test_read_one_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we read one asset
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.get(url_for('events.read_one_asset', asset_id = asset_id))
    # THEN we should have the correct status code
    assert resp.status_code == 200
    # THEN the asset should end up with the correct attribute
    asset = auth_client.sqla.query(Asset).filter(Asset.id == asset_id).first()
    assert resp.json["description"] == asset.description
    assert resp.json["active"] == asset.active
    # WHEN we try to read an asset that doesn't exist
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.get(url_for('events.read_one_asset', asset_id = -99))
    # THEN we expect an error
    assert resp.status_code == 404
    


@pytest.mark.smoke
def test_read_one_missing_asset(auth_client):
    # GIVEN an empty database
    # WHEN we read one asset
    resp = auth_client.get(url_for('events.read_one_asset', asset_id = 1))
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
    resp = auth_client.put(url_for('events.update_asset', asset_id = asset_id), json={
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
    resp = auth_client.put(url_for('events.update_asset', asset_id = asset_id), json=json_request)
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
    resp = auth_client.patch(url_for('events.update_asset', asset_id = asset_id), json={
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
def test_delete_asset(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
    # WHEN we delete one from it
    deleting_id = auth_client.sqla.query(Asset.id).first()[0]
    resp = auth_client.delete(url_for('events.delete_asset', asset_id = deleting_id))
    # THEN we should have the correct status code
    assert resp.status_code == 204
    # THEN we should have the asset as inactive
    isActive = auth_client.sqla.query(Asset.active).filter(Asset.id == deleting_id).first()[0]
    assert isActive == False
    

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
def test_read_all_team_members(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    
    # WHEN
    create_teams_members(auth_client.sqla)
    teams = auth_client.sqla.query(Team).all()

    for team in teams:
        members = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team.id).all()
        
        # THEN
        resp = auth_client.get(url_for('events.read_all_team_members', team_id = team.id))
        assert resp.status_code == 200

        for member in members:
            in_team = False
            team_ids = get_team_ids(resp.json[str(member.member_id)]['teams'])
            assert team.id in team_ids


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


# ---- Linking tables (asset <-> event)

@pytest.mark.smoke
def test_add_asset_to_event(auth_client):
    # GIVEN a database with some events and assets
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    count_assets = random.randint(15, 20)
    count_events = random.randint(3, 5)
    create_multiple_assets(auth_client.sqla, count_assets)
    create_multiple_events(auth_client.sqla, count_events)
    # WHEN we create an asset to an event
    for _ in range(count_assets):
        test_asset_id = random.randint(1, count_assets)
        test_event_id = random.randint(1, count_events + 1)
        test_asset = auth_client.sqla.query(Asset).filter(Asset.id == test_asset_id).first()
        test_event = auth_client.sqla.query(Event).filter(Event.id == test_event_id).first()
        resp = auth_client.put(url_for('events.add_asset_to_event', asset_id = test_asset_id, event_id = test_event_id))
        if not test_event:
            assert resp.status_code == 404
            continue

        test_asset_events = auth_client.sqla.query(Event).join(EventAsset).filter_by(asset_id=test_asset_id).all()
        for asset_event in test_asset_events:
            # test for overlap with existing events
            if test_event.start <= asset_event.start < test_event.end \
            or asset_event.start <= test_event.start < asset_event.end \
            or test_event.start < asset_event.end <= test_event.end \
            or asset_event.start < test_event.end <= asset_event.end:
                assert resp.status_code == 422
                continue

    # THEN we expect the right status code
        assert resp.status_code == 200
    # THEN we expect the entry in the database's linking table
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == 1
    # WHEN we create the eventAsset again
    resp = auth_client.post(url)
    # THEN we expect an error code
    assert resp.status_code == 422

@pytest.mark.smoke
def test_add_asset_to_invalid_event(auth_client):
    # GIVEN a database with some events and assets
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    create_multiple_assets(auth_client.sqla, 1)
    create_multiple_events(auth_client.sqla, 1)
    # WHEN we create an asset to an event that doesn't exist
    invalid_event_id = auth_client.sqla.query(Event.id).first()[0] + 1
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.add_asset_to_event', event_id=invalid_event_id, asset_id=asset_id)
    resp = auth_client.post(url)
    # THEN we expect the right status code
    assert resp.status_code == 404
    # THEN we don't expect the entry in the database's linking table
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(EventAsset.event_id == invalid_event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == 0

@pytest.mark.smoke
def test_add_booked_asset_to_event(auth_client):
    # GIVEN a database with some events and assets linked
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    create_multiple_assets(auth_client.sqla, 1)
    create_multiple_events(auth_client.sqla, 2)
    create_events_assets(auth_client.sqla, 1)

    event_id = auth_client.sqla.query(Event.id).first()[0]
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    # WHEN we create an asset to an event
    url = url_for('events.add_asset_to_event', event_id=event_id, asset_id=asset_id)
    resp = auth_client.post(url)
    # THEN we expect the right status code
    assert resp.status_code == 422
    # THEN we expect the entry not to be duplicated in the database's linking table
    new_queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == new_queried_event_asset_count

@pytest.mark.smoke
def test_remove_asset_from_event(auth_client):
    # GIVEN a database with some linked events and assets
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    create_multiple_assets(auth_client.sqla, 5)
    create_multiple_events(auth_client.sqla, 5)
    create_events_assets(auth_client.sqla, 1)
    link_count = auth_client.sqla.query(EventAsset).count()
    # WHEN we unlink an asset from an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.remove_asset_from_event', event_id=event_id, asset_id=asset_id)
    resp = auth_client.delete(url)
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the number of entries in the database's linking table to be one less
    new_link_count = auth_client.sqla.query(EventAsset).count()
    assert new_link_count == link_count - 1
    # WHEN we unlink the same asset
    resp = auth_client.delete(url)
    # THEN We expect an error
    assert resp.status_code == 404

@pytest.mark.smoke
def test_remove_unbooked_asset_from_event(auth_client):
    # GIVEN a database with some linked events and assets
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    create_multiple_assets(auth_client.sqla, 5)
    create_multiple_events(auth_client.sqla, 5)
    create_events_assets(auth_client.sqla, 1)
    link_count = auth_client.sqla.query(EventAsset).count()
    # WHEN we unlink an asset from an event
    invalid_event_id = 15000000000
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.remove_asset_from_event', event_id=invalid_event_id, asset_id=asset_id)
    resp = auth_client.delete(url)
    # THEN we expect the right status code
    assert resp.status_code == 404
    # THEN we expect the number of entries in the database's linking table to be one less
    new_link_count = auth_client.sqla.query(EventAsset).count()
    assert new_link_count == link_count


# ---- Linking tables (event <-> team)

@pytest.mark.smoke
def test_get_event_teams(auth_client):
    # GIVEN a database with some linked events and teams
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_teams(auth_client.sqla, 5)
    create_events_teams(auth_client.sqla, 1)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    link_count = auth_client.sqla.query(EventTeam).filter(EventTeam.event_id == event_id).count()
    # WHEN we get the teams associated with an event
    resp = auth_client.get(url_for('events.get_event_teams', event_id=event_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of teams
    assert len(resp.json) == link_count
    # THEN we expect each entry in the returned array to correspond to one entry in the database
    for team in resp.json:
        queried_event_team_count = auth_client.sqla.query(EventTeam).filter(EventTeam.event_id == event_id, EventTeam.team_id == team["id"]).count()
        assert queried_event_team_count == 1


@pytest.mark.smoke
def test_add_event_team(auth_client):
    # GIVEN a database with only some teams
    create_multiple_teams(auth_client.sqla, 5)
    team_id = auth_client.sqla.query(Team.id).first()[0]
    # WHEN we try to link a non-existant event to a team
    resp = auth_client.post(url_for('events.add_event_team', event_id=1, team_id=team_id))
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and teams
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we link a team with an event
    resp = auth_client.post(url_for('events.add_event_team', event_id=event_id, team_id=team_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and team in the database
    count = auth_client.sqla.query(EventTeam).filter(EventTeam.event_id == event_id, EventTeam.team_id == team_id).count()
    assert count == 1
    # WHEN we link the same team again
    resp = auth_client.post(url_for('events.add_event_team', event_id=event_id, team_id=team_id))
    # THEN we expect an error status code
    assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_event_team(auth_client):
    # GIVEN a database with some linked events and teams
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_teams(auth_client.sqla, 5)
    create_events_teams(auth_client.sqla, 1)
    event_team = auth_client.sqla.query(EventTeam).first()
    count = auth_client.sqla.query(EventTeam).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for('events.delete_event_team', event_id=event_team.event_id, team_id=event_team.team_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventTeam).filter(EventTeam.event_id == event_team.event_id, EventTeam.team_id == event_team.team_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventTeam).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_event_team', event_id=event_team.event_id, team_id=event_team.team_id))
    # THEN we expect an error
    assert resp.status_code == 404

# ---- Linking tables (event <-> person)

@pytest.mark.smoke
def test_get_event_persons(auth_client):
    # GIVEN a database with some linked events and persons
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_persons(auth_client.sqla, 1)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    link_count = auth_client.sqla.query(EventPerson).filter(EventPerson.event_id == event_id).count()
    # WHEN we get the persons associated with an event
    resp = auth_client.get(url_for('events.get_event_persons', event_id=event_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of persons
    assert len(resp.json) == link_count
    # THEN we expect each entry in the returned array to correspond to one entry in the database
    for person in resp.json:
        queried_event_person_count = auth_client.sqla.query(EventPerson).filter(EventPerson.event_id == event_id, EventPerson.person_id == person["person_id"]).count()
        assert queried_event_person_count == 1

@pytest.mark.smoke
def test_add_event_persons(auth_client):
    dscrptn = fake.sentences(nb=1)[0]
    payload = {
            'description': dscrptn
    }
    # GIVEN a database with only some persons
    create_multiple_people(auth_client.sqla, 5)
    person_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existant event to a person
    resp = auth_client.post(url_for('events.add_event_persons', event_id=1, person_id=person_id), json=payload)
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and persons
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we try to make a link without description
    resp = auth_client.post(url_for('events.add_event_persons', event_id=1, person_id=person_id))
    # THEN we expect an error code
    assert resp.status_code == 422
    # WHEN we link a person with an event
    resp = auth_client.post(url_for('events.add_event_persons', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and person in the database
    count = auth_client.sqla.query(EventPerson).filter(EventPerson.event_id == event_id, EventPerson.person_id == person_id).count()
    assert count == 1
    # WHEN we link the same person again
    resp = auth_client.post(url_for('events.add_event_persons', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error status code
    assert resp.status_code == 422

@pytest.mark.smoke
def test_modify_event_person(auth_client):
    dscrptn = fake.sentences(nb=1)[0]
    payload = {
            'description': dscrptn
    }
    # GIVEN a database with unlinked events and persons
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    # WHEN we try to modify a person not assiciated with an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    person_id = auth_client.sqla.query(Person.id).first()[0]
    resp = auth_client.patch(url_for('events.modify_event_person', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error
    assert resp.status_code == 404
    # GIVEN a database with some linked events and persons
    create_events_persons(auth_client.sqla, 1)
    event_person = auth_client.sqla.query(EventPerson).first()
    # WHEN we try to modify an event_person without a payload
    resp = auth_client.patch(url_for('events.modify_event_person', event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect the error code
    assert resp.status_code == 422
    # WHEN we modify an event_person
    resp = auth_client.patch(url_for('events.modify_event_person', event_id=event_person.event_id, person_id=event_person.person_id), json=payload)
    # THEN we expect the correct code
    assert resp.status_code == 200
    # THEN we expect the event_person to be modified
    queried_description = auth_client.sqla.query(EventPerson.description).filter(EventPerson.event_id == event_person.event_id, EventPerson.person_id == event_person.person_id).first()[0]
    assert queried_description == dscrptn

@pytest.mark.smoke
def test_delete_event_persons(auth_client):
    # GIVEN a database with some linked events and persons
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_persons(auth_client.sqla, 1)
    event_person = auth_client.sqla.query(EventPerson).first()
    count = auth_client.sqla.query(EventPerson).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for('events.delete_event_persons', event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventPerson).filter(EventPerson.event_id == event_person.event_id, EventPerson.person_id == event_person.person_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventPerson).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_event_persons', event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect an error
    assert resp.status_code == 404

# ---- Linking tables (event <-> participant)

@pytest.mark.smoke
def test_get_event_participants(auth_client):
    # GIVEN a database with some linked events and participants
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_participants(auth_client.sqla, 1)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    link_count = auth_client.sqla.query(EventParticipant).filter(EventParticipant.event_id == event_id).count()
    # WHEN we get the participants associated with an event
    resp = auth_client.get(url_for('events.get_event_participants', event_id=event_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of participants
    assert len(resp.json) == link_count
    # THEN we expect each entry in the returned array to correspond to one entry in the database
    for participant in resp.json:
        queried_event_participant_count = auth_client.sqla.query(EventParticipant).filter(EventParticipant.event_id == event_id, EventParticipant.person_id == participant["person_id"]).count()
        assert queried_event_participant_count == 1

@pytest.mark.smoke
def test_add_event_participants(auth_client):
    payload = {
            'confirmed': flip()
    }
    # GIVEN a database with only some participants
    create_multiple_people(auth_client.sqla, 5)
    person_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existant event to a participant
    resp = auth_client.post(url_for('events.add_event_participants', event_id=1, person_id=person_id), json=payload)
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and participants
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we try to make a link without description
    resp = auth_client.post(url_for('events.add_event_participants', event_id=1, person_id=person_id))
    # THEN we expect an error code
    assert resp.status_code == 422
    # WHEN we link a participant with an event
    resp = auth_client.post(url_for('events.add_event_participants', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and participant in the database
    count = auth_client.sqla.query(EventParticipant).filter(EventParticipant.event_id == event_id, EventParticipant.person_id == person_id).count()
    assert count == 1
    # WHEN we link the same participant again
    resp = auth_client.post(url_for('events.add_event_participants', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error status code
    assert resp.status_code == 422

@pytest.mark.smoke
def test_modify_event_participant(auth_client):
    payload = {
            'confirmed': flip()
    }
    # GIVEN a database with unlinked events and participants
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    # WHEN we try to modify a participant not assiciated with an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    person_id = auth_client.sqla.query(Person.id).first()[0]
    resp = auth_client.patch(url_for('events.modify_event_participant', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error
    assert resp.status_code == 404
    # GIVEN a database with some linked events and participants
    create_events_participants(auth_client.sqla, 1)
    event_participant = auth_client.sqla.query(EventParticipant).first()
    # WHEN we try to modify an event_participant without a payload
    resp = auth_client.patch(url_for('events.modify_event_participant', event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect the error code
    assert resp.status_code == 422
    # WHEN we modify an event_participant
    resp = auth_client.patch(url_for('events.modify_event_participant', event_id=event_participant.event_id, person_id=event_participant.person_id), json=payload)
    # THEN we expect the correct code
    assert resp.status_code == 200
    # THEN we expect the event_participant to be modified
    queried_confirmed = auth_client.sqla.query(EventParticipant.confirmed).filter(EventParticipant.event_id == event_participant.event_id, EventParticipant.person_id == event_participant.person_id).first()[0]
    assert queried_confirmed == payload["confirmed"]

@pytest.mark.smoke
def test_delete_event_participant(auth_client):
    # GIVEN a database with some linked events and participants
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_participants(auth_client.sqla, 1)
    event_participant = auth_client.sqla.query(EventParticipant).first()
    count = auth_client.sqla.query(EventParticipant).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for('events.delete_event_participant', event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventParticipant).filter(EventParticipant.event_id == event_participant.event_id, EventParticipant.person_id == event_participant.person_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventParticipant).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_event_participant', event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect an error
    assert resp.status_code == 404

# ---- Linking tables (team <-> member)

@pytest.mark.smoke
def test_get_team_members(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    create_teams_members(auth_client.sqla)
    
    # WHEN
    teams = auth_client.sqla.query(Team).all()
    
    for team in teams:
        members = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team.id).all()
        
        # THEN
        resp = auth_client.get(url_for('events.get_team_members', team_id = team.id))

        assert resp.status_code == 200
        assert len(resp.json) == len(members)


@pytest.mark.smoke
def test_get_team_members_no_members(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)

    # WHEN
    teams = auth_client.sqla.query(Team).all()

    for team in teams:
        resp = auth_client.get(url_for('events.get_team_members', team_id = team.id))

        assert resp.status_code == 404

@pytest.mark.smoke
def test_add_team_member(auth_client):
    # GIVEN a database with only some members
    create_multiple_people(auth_client.sqla, 5)
    member_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existant team to a member
    resp = auth_client.post(url_for('events.add_team_member', team_id=1, member_id=member_id))
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked teams and members
    create_multiple_teams(auth_client.sqla, 5)
    team_id = auth_client.sqla.query(Team.id).first()[0]
    # WHEN we link a member with an team
    resp = auth_client.post(url_for('events.add_team_member', team_id=team_id, member_id=member_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked team and member in the database
    count = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.member_id == member_id).count()
    assert count == 1
    # WHEN we link the same member again
    resp = auth_client.post(url_for('events.add_team_member', team_id=team_id, member_id=member_id))
    # THEN we expect an error status code
    assert resp.status_code == 422


@pytest.mark.smoke
def test_modify_team_member(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    
    # WHEN
    create_teams_members(auth_client.sqla)
    team_members = auth_client.sqla.query(TeamMember).all()

    for team_member in team_members:
        f = flip()
        resp = auth_client.patch(url_for('events.modify_team_member', team_id = team_member.team_id, member_id = team_member.member_id), json = {'active':f})
        
        assert resp.status_code == 200
        assert resp.json['active'] == f


@pytest.mark.smoke
def test_modify_team_member_invalid(auth_client):
    # GIVEN
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    
    # WHEN
    create_teams_members(auth_client.sqla)
    team_members = auth_client.sqla.query(TeamMember).all()

    for team_member in team_members:
        resp = auth_client.patch(url_for('events.modify_team_member', team_id = team_member.team_id, member_id = team_member.member_id), json = {'team_id':10})

        assert resp.status_code == 422


def test_delete_team_member(auth_client):
    # GIVEN a database with some linked teams and members
    create_multiple_teams(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_teams_members(auth_client.sqla, 1)
    team_member = auth_client.sqla.query(TeamMember).first()
    count = auth_client.sqla.query(TeamMember).count()
    # WHEN we unlink an assets from an team
    resp = auth_client.delete(url_for('events.delete_team_member', team_id=team_member.team_id, member_id=team_member.member_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be inactive in the database
    assert 1 == auth_client.sqla.query(TeamMember).filter(TeamMember.active == False, TeamMember.team_id == team_member.team_id, TeamMember.member_id == team_member.member_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(TeamMember).filter(TeamMember.active == True).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_team_member', team_id=team_member.team_id, member_id=team_member.member_id))
    # THEN we expect an error
    assert resp.status_code == 404



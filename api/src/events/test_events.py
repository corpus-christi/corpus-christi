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
from .create_event_data import flip, fake, create_multiple_events, event_object_factory, create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, create_events_persons, create_teams_members, get_team_ids
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
        if flip() and event.active:
            print("Delete with id:" + str(event.id))
            resp = auth_client.delete(url_for('events.delete_event', event_id = event.id))
            print(event.active)
            #print(resp.json['active'])
            #print(resp.json)
            #assert resp.status_code == 200
            deleted += 1
        elif not event.active:
            deleted += 1

    new_events = auth_client.sqla.query(Event).filter(Event.active == True).all()
    assert len(new_events) == count - deleted
    

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
def test_read_all_assets(auth_client):
    # GIVEN a database with some assets
    generate_locations(auth_client)
    count = random.randint(5, 15)
    create_multiple_assets(auth_client.sqla, count)
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


# ---- Linking tables

@pytest.mark.smoke
def test_add_asset_to_event(auth_client):
    # GIVEN a database with some events and assets
    generate_locations(auth_client)
    location_id = auth_client.sqla.query(Location.id).first()[0]
    create_multiple_assets(auth_client.sqla, 1)
    create_multiple_events(auth_client.sqla, 1)
    # WHEN we create an asset to an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.add_asset_to_event', event_id=event_id, asset_id=asset_id)
    resp = auth_client.post(url)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the entry in the database's linking table
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == 1

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


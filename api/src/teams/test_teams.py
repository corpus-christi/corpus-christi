import pytest
import random
import datetime
import random
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from ..events.create_event_data import flip, fake, create_multiple_events, event_object_factory, email_object_factory, create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, create_events_persons, create_events_participants, create_teams_members, get_team_ids, asset_object_factory, team_object_factory
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas
from ..people.test_people import create_multiple_people

from ..people.models import Person, PersonSchema
from .models import Team, TeamMember, TeamSchema, TeamMemberSchema

# ---- Team


@pytest.mark.smoke
def test_create_team(auth_client):
    # GIVEN a database
    # WHEN we create a team
    new_team = {
            'description': fake.sentences(nb=1)[0],
            'active': flip()
    }
    resp = auth_client.post(url_for('teams.create_team'), json=new_team)
    # THEN we expect the right status code
    assert resp.status_code == 201
    # THEN we expect the correct attributes of the given team in the database
    queried_team = auth_client.sqla.query(Team).filter(Team.id == resp.json["id"]).first()
    for attr in new_team:
        assert new_team[attr] == queried_team.__dict__[attr]

    # WHEN we create an invalid team
    if flip():
        new_team['description'] = None
    else:
        new_team['active'] = None
    resp = auth_client.post(url_for('teams.create_team'), json=new_team)
    # THEN the response should have the correct code
    assert resp.status_code == 422
    

@pytest.mark.smoke
def test_read_all_teams(auth_client):
    # GIVEN a database with a number of pre-defined teams
    teams = []
    count = random.randint(5, 15)
    for i in range(count):
        tmp_team = team_object_factory()
        if i == 0:
            tmp_team["description"] = "the most awesome team"
            tmp_team['active'] = True
        else:
            tmp_team["description"] = "nothing to be filtered"
        teams.append(Team(**TeamSchema().load(tmp_team)))
    auth_client.sqla.add_all(teams)
    auth_client.sqla.commit()
    # WHEN we try to read all teams with a filter 'drum'
    filtered_teams = auth_client.get(url_for('teams.read_all_teams', return_group="all", desc="awesome", sort='description_desc')).json
    # THEN we should have exactly one team
    assert len(filtered_teams) == 1
    # GIVEN a database with some teams
    # WHEN we read all active ones
    active_teams = auth_client.get(url_for('teams.read_all_teams')).json
    queried_active_teams_count = auth_client.sqla.query(Team).filter(Team.active==True).count()
    # THEN we should have the same amount as we do in the database
    assert len(active_teams) == queried_active_teams_count
    # THEN for each team, the attributes should match
    for team in active_teams:
        queried_team = auth_client.sqla.query(Team).filter(Team.id == team["id"]).first()
        assert queried_team.description == team["description"]
        assert queried_team.active == team["active"]
    # WHEN we read all teams (active and inactive)
    all_teams = auth_client.get(url_for('teams.read_all_teams', return_group="all")).json
    # THEN we should have the same number
    assert len(all_teams) == count
    # WHEN we ask for all inactive teams
    inactive_teams = auth_client.get(url_for('teams.read_all_teams', return_group="inactive")).json
    queried_inactive_teams_count = auth_client.sqla.query(Team).filter(Team.active==False).count()
    # THEN we should have the correct number of inactive teams
    assert len(inactive_teams) == queried_inactive_teams_count
    # WHEN we ask for a description match
    teams = auth_client.get(url_for('teams.read_all_teams', desc='c')).json
    # THEN we should have results that match that description
    for team in teams:
        assert 'c' in team['description'].lower()
    

@pytest.mark.smoke
def test_read_one_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we read one team
    team_id = auth_client.sqla.query(Team.id).first()[0]
    resp = auth_client.get(url_for('teams.read_one_team', team_id = team_id))
    # THEN we should have the correct status code
    assert resp.status_code == 200
    # THEN the team should end up with the correct attribute
    team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert resp.json["description"] == team.description
    assert resp.json["active"] == team.active
    # WHEN we read a missing team
    resp = auth_client.get(url_for('teams.read_one_team', team_id = 42))
    # THEN the response should be an error
    assert resp.status_code == 404
    

@pytest.mark.smoke
def test_read_all_team_members(auth_client):
    # GIVEN a database with some linked teams and members
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    create_teams_members(auth_client.sqla)
    
    # WHEN we read all members for each team
    teams = auth_client.sqla.query(Team).all()

    for team in teams:
        members = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team.id).all()
        
        resp = auth_client.get(url_for('teams.read_all_team_members', team_id = team.id))
        # THEN we expect a correct status code
        assert resp.status_code == 200

        # THEN we expect for each member of the team, the current team's id is in the member's "teams"
        for member in members:
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
    resp = auth_client.put(url_for('teams.replace_team', team_id = team_id), json={
        'description': dscrptn,
        'active': False
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the team should end up with the correct attribute
    new_team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert new_team.description == dscrptn
    assert new_team.active == False
    # WHEN we replace with an invalid object
    resp = auth_client.put(url_for('teams.replace_team', team_id = team_id), json={})
    # THEN the response should be an error
    

@pytest.mark.smoke
def test_update_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we update one team
    team_id = auth_client.sqla.query(Team.id).first()[0]
    dscrptn = fake.sentences(nb=1)[0]
    resp = auth_client.patch(url_for('teams.update_team', team_id = team_id), json={
        'description': dscrptn,
        'active': False
    })
    # THEN we should have the correct status code
    assert resp.status_code == 200 
    # THEN the team should end up with the correct attribute
    new_team = auth_client.sqla.query(Team).filter(Team.id == team_id).first()
    assert new_team.description == dscrptn
    assert new_team.active == False
    # WHEN we update with an invalid object
    json_object = {
        'description': dscrptn,
        'active': False
    }
    if flip():
        json_object['description'] = None
    else:
        json_object['active'] = None
    resp = auth_client.patch(url_for('teams.update_team', team_id = team_id), json=json_object)
    # THEN the response should be an error
    assert resp.status_code == 422
    

@pytest.mark.smoke
def test_delete_team(auth_client):
    # GIVEN a database with some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we delete one from it
    deleting_id = auth_client.sqla.query(Team.id).first()[0]
    resp = auth_client.delete(url_for('teams.delete_team', team_id = deleting_id))
    # THEN we should have the correct status code
    assert resp.status_code == 204
    # THEN we should have the team as inactive
    isActive = auth_client.sqla.query(Team.active).filter(Team.id == deleting_id).first()[0]
    assert isActive == False
    # WHEN we delete a missing team
    resp = auth_client.delete(url_for('teams.delete_team', team_id = 42))
    # THEN the response should be an error
    assert resp.status_code == 404

# ---- Linking tables (team <-> member)

@pytest.mark.smoke
def test_get_team_members(auth_client):
    # GIVEN a database with a number of connected team and members
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    create_teams_members(auth_client.sqla)
    
    # WHEN we ask for the members associated with each team
    teams = auth_client.sqla.query(Team).all()
    for team in teams:
        members = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team.id).all()
        
        resp = auth_client.get(url_for('teams.get_team_members', team_id = team.id))

        # THEN we assume the correct status code
        assert resp.status_code == 200
        # THEN we assume the right amount of members associated with the team
        assert len(resp.json) == len(members)


@pytest.mark.smoke
def test_get_team_members_no_members(auth_client):
    # GIVEN a database with only some teams
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    # WHEN we ask for TeamMembers
    teams = auth_client.sqla.query(Team).all()
    for team in teams:
        resp = auth_client.get(url_for('teams.get_team_members', team_id = team.id))
        # THEN we expect an error
        assert resp.status_code == 404

@pytest.mark.smoke
def test_add_team_member(auth_client):
    # GIVEN a database with only some members
    create_multiple_people(auth_client.sqla, 5)
    member_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existant team to a member
    resp = auth_client.post(url_for('teams.add_team_member', team_id=1, member_id=member_id), json={'active': flip()})
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked teams and members
    create_multiple_teams(auth_client.sqla, 5)
    team_id = auth_client.sqla.query(Team.id).first()[0]
    # WHEN we link a member with an team
    resp = auth_client.post(url_for('teams.add_team_member', team_id=team_id, member_id=member_id), json={'active': flip()})
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked team and member in the database
    count = auth_client.sqla.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.member_id == member_id).count()
    assert count == 1
    # WHEN we link the same member again
    resp = auth_client.post(url_for('teams.add_team_member', team_id=team_id, member_id=member_id), json={'active': flip()})
    # THEN we expect an error status code
    assert resp.status_code == 422
    # WHEN we link an invalid person
    resp = auth_client.post(url_for('teams.add_team_member', team_id=team_id, member_id=42), json={'active': flip()})
    # THEN we expect an error status code
    assert resp.status_code == 404

@pytest.mark.smoke
def test_add_team_member_invalid(auth_client):
    # GIVEN a database with only some members
    create_multiple_people(auth_client.sqla, 5)
    member_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existant team to a member
    resp = auth_client.post(url_for('teams.add_team_member', team_id=1, member_id=member_id))
    # THEN we expect an error code
    assert resp.status_code == 422

@pytest.mark.smoke
def test_modify_team_member(auth_client):
    # GIVEN a database with some linked teams and people
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    create_teams_members(auth_client.sqla)
    
    # WHEN we modify each teamMember
    team_members = auth_client.sqla.query(TeamMember).all()

    for team_member in team_members:
        f = flip()
        resp = auth_client.patch(url_for('teams.modify_team_member', team_id = team_member.team_id, member_id = team_member.member_id), json = {'active':f})
        
        # THEN we expect the right status code
        assert resp.status_code == 200
        # THEN we expect the correct content in the TeamMember
        assert resp.json['active'] == f


@pytest.mark.smoke
def test_modify_team_member_invalid(auth_client):
    # GIVEN a database with some linked teamMembers
    count = random.randint(5, 15)
    create_multiple_teams(auth_client.sqla, count)
    person_count = random.randint(20, 30)
    create_multiple_people(auth_client.sqla, count)
    create_teams_members(auth_client.sqla)
    
    # WHEN we try to modify the content with an invalid payload
    team_members = auth_client.sqla.query(TeamMember).all()

    for team_member in team_members:
        resp = auth_client.patch(url_for('teams.modify_team_member', team_id = team_member.team_id, member_id = team_member.member_id), json = {'invalid_field': 10})
        # THEN we expect an error
        assert resp.status_code == 422

    # WHEN we modify a team member that doesn't exist
    resp = auth_client.patch(url_for('teams.modify_team_member', team_id = 42, member_id = 429), json = {'active': flip()})
    # THEN the response should be an errror
    assert resp.status_code == 404


@pytest.mark.smoke
def test_delete_team_member(auth_client):
    # GIVEN a database with some linked teams and members
    create_multiple_teams(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_teams_members(auth_client.sqla, 1)
    team_member = auth_client.sqla.query(TeamMember).filter(TeamMember.active == True).first()
    count = auth_client.sqla.query(TeamMember).filter(TeamMember.active == True).count()
    # WHEN we unlink an assets from an team
    resp = auth_client.delete(url_for('teams.delete_team_member', team_id=team_member.team_id, member_id=team_member.member_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be inactive in the database
    assert 1 == auth_client.sqla.query(TeamMember).filter(TeamMember.active == False, TeamMember.team_id == team_member.team_id, TeamMember.member_id == team_member.member_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(TeamMember).filter(TeamMember.active == True).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('teams.delete_team_member', team_id=team_member.team_id, member_id=team_member.member_id))
    # THEN we expect an error
    assert resp.status_code == 422
    # WHEN we unlink using an invalid person
    resp = auth_client.delete(url_for('teams.delete_team_member', team_id=429, member_id=team_member.member_id))
    # THEN we expect an error
    assert resp.status_code == 404

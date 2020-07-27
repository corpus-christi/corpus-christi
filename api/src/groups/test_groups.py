import random

import pytest
from dateutil import parser
from faker import Faker
from flask import url_for

from .create_group_data import flip, group_object_factory, \
    create_multiple_groups, member_object_factory, create_multiple_members, meeting_object_factory, \
    create_multiple_meetings, create_multiple_attendance, create_multiple_group_types, create_multiple_manager_types, \
    group_type_object_factory, manager_type_object_factory, create_multiple_managers, \
    create_hierarchy_test_case_1
from .group_hierarchy_helpers import get_all_subgroups
from .models import Group, GroupType, Member, Meeting, MeetingSchema, Attendance, Manager, ManagerType, ManagerSchema
from ..images.create_image_data import create_images_groups
from ..images.create_image_data import create_test_images
from ..images.models import Image, ImageGroup
from ..people.test_people import create_multiple_people, role_object_factory, person_object_factory
from ..people.models import Person, PersonSchema, Role, RoleSchema
from ..places.models import Address, Country
from ..places.test_places import create_multiple_addresses, create_multiple_areas
from flask_jwt_extended import create_access_token

fake = Faker()

# ---- Group Type

@pytest.mark.smoke
def test_create_group_type(auth_client):
    # GIVEN an empty database
    # WHEN we add in a group type
    resp = auth_client.post(url_for('groups.create_group_type'), json = {'name':'group_type_1'})
    # THEN expect the create to run OK
    assert resp.status_code == 201
    # THEN we expect the correct number of items in the database
    assert auth_client.sqla.query(GroupType).count() == 1

def test_create_invalid_group_type(auth_client):
    # GIVEN an empty database
    # WHEN we add in an invalid group type
    resp = auth_client.post(url_for('groups.create_group_type'), json = {'name':''})
    # THEN we expect the request to be unprocessable
    assert resp.status_code == 422

@pytest.mark.smoke
def test_read_one_group_type(auth_client):
    # GIVEN a database with a number of group types
    count = random.randint(3, 11)
    create_multiple_group_types(auth_client.sqla, count)
    group_types = auth_client.sqla.query(GroupType).all()
    # WHEN we ask for the group_types one by one
    for group_type in group_types:
        # THEN we expect each of them to correspond to the group_type in the database
        resp = auth_client.get(
            url_for('groups.read_one_group_type', group_type_id=group_type.id))
        assert resp.status_code == 200
        assert resp.json['name'] == group_type.name
    
@pytest.mark.smoke
def test_read_all_group_types(auth_client):
    # GIVEN a database with some group_types
    count = random.randint(3, 11)
    create_multiple_group_types(auth_client.sqla, count)

    # WHEN we read all active group_types
    resp = auth_client.get(url_for('groups.read_all_group_types'))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the database has the same number of group_types as we created
    group_types = auth_client.sqla.query(GroupType).all()
    assert len(group_types) == count

@pytest.mark.smoke
def test_update_group_type(auth_client):
    # GIVEN a database with a number of group_types
    count = random.randint(3, 11)
    create_multiple_group_types(auth_client.sqla, count)

    # WHEN we update one group_type
    group_type = auth_client.sqla.query(GroupType).first()

    payload = group_type_object_factory("new_name")

    resp = auth_client.patch(
        url_for('groups.update_group_type', group_type_id=group_type.id), json=payload)

    # THEN we assume the correct status code
    assert resp.status_code == 200
    # THEN we assume the correct content in the returned object
    assert resp.json['name'] == 'new_name'
    # THEN we assume the correct content in the database
    assert auth_client.sqla.query(GroupType).filter_by(id=group_type.id).first().name == 'new_name'

@pytest.mark.smoke
def test_delete_group_type(auth_client):
    # GIVEN a database with a number of group_types
    count = random.randint(3, 11)
    create_multiple_group_types(auth_client.sqla, count)

    # WHEN we delete one of them
    group_type = auth_client.sqla.query(GroupType).first()
    resp = auth_client.delete(url_for('groups.delete_group_type', group_type_id = group_type.id))
    # THEN we assume the correct status code
    assert resp.status_code == 204

    # WHEN we delete a non-existent item
    resp = auth_client.delete(url_for('groups.delete_group_type', group_type_id = -1))
    # THEN we expect an error
    assert resp.status_code == 404

    # THEN we assume the number of group_types in the database to be the correct number
    group_types = auth_client.sqla.query(GroupType).all()
    assert len(group_types) == count - 1

# # ---- Group
def test_create_valid_group(auth_client):
    # Test creating valid group
    # GIVEN an existing group
    count = random.randint(8, 19)
    create_multiple_group_types(auth_client.sqla, 1)
    group_type = auth_client.sqla.query(GroupType).first()
    # WHEN one or more groups need a section
    for i in range(count):
        resp = auth_client.post(url_for(
            'groups.create_group'), json=group_object_factory(group_type.id))
        assert resp.status_code == 201

def test_create_invalid_group(auth_client):
    # Test creating invalid group
    # GIVEN invalid group to put in database
    broken_group = {}
    # WHEN database queried
    resp = auth_client.post(
        url_for('groups.create_group'), json=broken_group)
    # THEN expect Unprocessable Entity response
    assert resp.status_code == 422
    create_multiple_group_types(auth_client.sqla, 1)
    group_type = auth_client.sqla.query(GroupType).first()
    # TEST with creating group invalid request
    group_type.id = -1
    resp = auth_client.post(url_for(
                'groups.create_group'), json=group_object_factory(group_type.id))
    # WHEN expect Not Found response
    assert resp.status_code == 404

@pytest.mark.smoke
def test_read_all_groups(auth_client):
    # GIVEN existing (active and inactive) group
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(8, 19)
    create_multiple_groups(auth_client.sqla, count)
    # WHEN all sections needed
    resp = auth_client.get(url_for('groups.create_group'))
    # THEN list all group sections
    assert len(resp.json) == count

@pytest.mark.smoke
def test_read_one_group(auth_client):
    # GIVEN an existing group
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    # WHEN one group section needed
    groups = auth_client.sqla.query(Group).all()
    # THEN list one group section of group
    for group in groups:
        resp = auth_client.get(url_for(
            'groups.read_one_group', group_id=group.id))
        assert resp.status_code == 200
        assert resp.json['name'] == group.name
        assert resp.json['description'] == group.description
        assert resp.json['active'] == group.active
        assert resp.json['groupTypeId'] == group.group_type_id

@pytest.mark.smoke
def test_update_group(auth_client):
    # TEST with valid group
    # GIVEN empty database
    # WHEN databse queried
    # TEST with populated database
    # GIVEN an existing (active or inactive) group
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    groups = auth_client.sqla.query(Group).all()
    # WHEN group needs to update existing information
    for group in groups:
        resp = auth_client.patch(url_for('groups.update_group', group_id=group.id),
                                 json={'name': 'asd', 'description': 'test_descr', 'active': False})
        # THEN assert changes to group  reflect update
        assert resp.status_code == 200
        assert resp.json['name'] == 'asd'
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False

def test_invalid_update_group(auth_client):
    # Test with invalid group
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(
        url_for('groups.update_group', group_id=555))
    # THEN assert error code
    assert resp.status_code == 422

def test_invalid_subset_group(auth_client):
    # Test with invalid subset with "offset"
    # GIVEN empty database
    # WHEN databse queried
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    # Test with populated database
    # GIVEN existing (active or inactive) groups
    groups = auth_client.sqla.query(Group).all()
    # WHEN there are difference between server and database assert error
    resp = auth_client.get(url_for('groups.create_group'))
    resp_offset = auth_client.get(url_for('groups.read_all_groups', offset=2))
    # Then give error if the response is invalid
    assert resp_offset.json[0]['id'] == groups[2].id
    # Test with invalid subset with "limit"
    resp_limit = auth_client.get(url_for('groups.read_all_groups', limit=2))
    assert len(resp_limit.json) == 2
    # Test 'offset' and 'limit' together
    resp_together = auth_client.get(url_for('groups.read_all_groups', offset=2, limit = 2))
    # THEN assert when either 'offset' or 'limit' doesn't work
    assert resp_together.json[0]['id'] == groups[2].id and len(resp_together.json)<=2

def test_subset_group_attributes(auth_client):
    # Test with different attribute(s)
    # GIVEN empty database
    # WHEN databse queried
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    # Test with invalid subset with a single matching attribute
    resp_a_attribute = auth_client.get(url_for('groups.read_all_groups', where='active:true'))
    for attribute in resp_a_attribute.json:
        assert attribute['active'] == True

    # Test with invalid subset with multiple matching attribute
    resp_multi_attribute = auth_client.get(url_for('groups.read_all_groups', where='active:true') + '&where=name:Not-exist-name')
    for attribute in resp_multi_attribute.json:
        assert attribute['active'] != True and attribute['name'] != 'Not-exist-name'

def test_subset_group_order(auth_client):
    # TEST to sort results use order in the URL query string by single attribute: "order = name:asc"
    # TEST retrieves all groups ordered ascending by name
    # GIVEN empty database
    # WHEN databse queried
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    # TEST with invalid subset with 'order'
    res_order_attribute = auth_client.get(url_for('groups.read_all_groups', order='name:asc'))
    first_letter=[]
    sorted_first_letter=[]
    # THEN put first letter into array
    for person in res_order_attribute.json:
        first_letter.append(person['name'][0])
    # TEST if the first letter array is sorted
    sorted_first_letter = sorted(first_letter)
    assert sorted_first_letter == first_letter

def test_subset_groups_descending_ascending(auth_client):
    # TEST to sort results use order in the URL query string by multiple attribute:
    # TEST retrieves all people, ordered ascending by last name, then descending by first name.
    # GIVEN empty database
    # WHEN databse queried
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)

    resp_asc_des = auth_client.get(url_for('groups.read_all_groups', order='group_type_id:asc') + '&order=id:desc')
    list_group_type_id = []
    sorted_group_type_id = []
    list_id = []
    sorted_id = []
    # THEN put group_type_id and id into array
    for person in resp_asc_des.json:
        list_group_type_id.append(person['groupTypeId'])
        list_id.append(person['id'])
    sorted_group_type_id = sorted(list_group_type_id)
    # TEST if the group_type_id is sorted in ascending
    assert sorted_group_type_id == list_group_type_id
    # TEST if the id is in descending order if the group_type_id (s) are the same
    right =  True
    for i in range(1 , len(list_id)):
        if sorted_group_type_id[i] == sorted_group_type_id[i-1] and list_id[i] <= list_id[i-1]:
            right = True
        else:
            right = False
    # Test if the id(s) are in descending order
        assert right == True

def test_activate_group(auth_client):
    # TEST with activate group
    # GIVEN empty database
    # WHEN databse queried
    # TEST with populated database
    # GIVEN an existing (active or inactive) group
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    groups = auth_client.sqla.query(Group).all()
    # WHEN group needs to active existing information
    for group in groups:
        resp = auth_client.patch(url_for('groups.update_group', group_id=group.id),
                                 json={'active': True})
        # THEN expect active is assigned with True
        assert resp.json['active'] == True

def test_deactivate_group(auth_client):
    # TEST with deactivate group
    # GIVEN empty database
    # WHEN databse queried
    # TEST with populated database
    # GIVEN an existing (active or inactive) group
    create_multiple_group_types(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_groups(auth_client.sqla, count)
    groups = auth_client.sqla.query(Group).all()
    # WHEN group needs to deactive existing information
    for group in groups:
        resp = auth_client.patch(url_for('groups.update_group', group_id=group.id),
                                 json={'active': False})
        # THEN expect active is assigned with False
        assert resp.json['active'] == False

# # ---- Meeting
@pytest.mark.smoke
def test_create_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we create a meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    meeting = auth_client.sqla.query(Meeting).all()
    address = auth_client.sqla.query(Address).first()
    group = auth_client.sqla.query(Group).first()
    # WHEN we creat a meeting with group information and address information
    resp = auth_client.post(url_for('groups.create_meeting'),
    json = meeting_object_factory(group_id=group.id, address_id=address.id))
    # THEN expect the create to run OK
    assert resp.status_code == 201

def test_create_invalid_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we create a invalid meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    address = auth_client.sqla.query(Address).first()
    group = auth_client.sqla.query(Group).first()
    # WHEN we creat an invalid meeting
    resp = auth_client.post(url_for('groups.create_meeting'),
    json = {'active': True, 'start_time':'-20' })
    # THEN expect error message
    assert resp.status_code == 422

@pytest.mark.smoke
def test_read_all_meetings(auth_client):
    # GIVEN an empty database
    # WHEN we read all meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    # WHEN we read all meetings
    resp = auth_client.get(url_for('groups.read_all_meetings'))
    assert resp.status_code == 200
    # WHEN we get all the meetings from database
    meeting = auth_client.sqla.query(Meeting).all()
    # THEN expect the same number of meetings
    assert len(resp.json) == len(meeting)

@pytest.mark.smoke
def test_read_one_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we read one meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    address = auth_client.sqla.query(Address).first()
    group = auth_client.sqla.query(Group).first()
    # WHEN we get one meeting
    first_meeting = auth_client.sqla.query(Meeting).first()
    resp = auth_client.get(url_for('groups.read_one_meeting', meeting_id=first_meeting.id))
    # THEN expect correct message
    assert resp.status_code == 200
    #WHEN the meeting doesn't exist
    resp = auth_client.get(url_for('groups.read_one_meeting', meeting_id=111))
    assert resp.status_code == 404

@pytest.mark.smoke
def test_update_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we update one meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    # WHEN we get one meeting
    first_meeting = auth_client.sqla.query(Meeting).first()
    # WHEN want to update the description
    resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=first_meeting.id), json= {'description': 'This is a tset'})
    # THEN expect correct message
    assert resp.json['description'] == 'This is a tset'

    #WHEN test activate meeting
    resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=first_meeting.id), json= {'active': True})
    assert resp.json['active'] == True
    #WHEN test deactivate meeting
    resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=first_meeting.id), json= {'active': False})
    assert resp.json['active'] == False

def test_invalid_update_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we update one meeting with invalid information
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    first_meeting = auth_client.sqla.query(Meeting).first()
    resp = auth_client.patch(url_for('groups.update_meeting', meeting_id=first_meeting.id), json= {'description': 123})
    assert resp.status_code == 422
    # AND check if the meeting is exist
    resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=333), json= {'description': 'Hello'})
    # THEN expect error code
    assert resp.status_code == 404

@pytest.mark.smoke
def test_delete_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we delete one meeting
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    # AND we get one meeting
    first_meeting = auth_client.sqla.query(Meeting).first()
    resp = auth_client.delete(url_for('groups.read_one_meeting', meeting_id=first_meeting.id))
    all_meetings = auth_client.sqla.query(Meeting).all()
    for one in all_meetings:
    # THEN we expect error code
        assert one.id != first_meeting.id

def test_delete_invalid_meeting(auth_client):
    # GIVEN an empty database
    # WHEN we update one meeting with invalid information
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_meetings(auth_client.sqla, 3)
    # WHEN we get one meeting
    first_meeting = auth_client.sqla.query(Meeting).first()
    resp = auth_client.delete(url_for('groups.read_one_meeting', meeting_id=123))
    assert resp.status_code == 404

def test_activate_meeting(auth_client):
    # GIVEN a database with active meetings and attendances
     create_multiple_groups(auth_client.sqla,1)
     create_multiple_meetings(auth_client.sqla, 3)
     # WHEN we get one meeting
     first_meeting = auth_client.sqla.query(Meeting).first()
     # WHEN we activate one meeting
     resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=first_meeting.id), json= {'active': True})
     # THEN we expect the meeting to be activated
     assert resp.json['active'] == True
     # WHEN we activate a non-existant meeting
     resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=-2), json= {'active': True})
     # THEN we expect an error code
     assert resp.status_code == 404

def test_deactivate_meeting(auth_client):
    # GIVEN a database with active meetings and attendances
     create_multiple_groups(auth_client.sqla,1)
     create_multiple_meetings(auth_client.sqla, 3)
     # WHEN we get one meeting
     first_meeting = auth_client.sqla.query(Meeting).first()
     # WHEN we deactivate one meeting
     resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=first_meeting.id), json= {'active': False})
     # THEN we expect the meeting to be deactivated
     assert resp.json['active'] == False
     # WHEN we deactivate a non-existant meeting
     resp = auth_client.patch(url_for('groups.read_one_meeting', meeting_id=-2), json= {'active': False})
     # THEN we expect an error code
     assert resp.status_code == 404

# # ---- Member
@pytest.mark.smoke
def test_create_member(auth_client):
    # GIVEN an empty database
    # WHEN we add in a member
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    personid = auth_client.sqla.query(Person).first().id
#     create_multiple_members(auth_client.sqla, 0.75)
    resp = auth_client.post(url_for('groups.create_member', group_id = '1'), json = {'personId':personid, 'active':'True', 'joined':'2020-01-01'})
    # THEN expect the create to run OK
    assert resp.status_code == 201

@pytest.mark.smoke
def test_read_all_members(auth_client):
    # GIVEN an empty database
    # WHEN we add in members
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    create_multiple_members(auth_client.sqla, fraction=0.75)
    # WHEN we test the number of members in the database, we compaer that with the request response
    count = len(auth_client.sqla.query(Member).all())
    # THEN we get the number of members from get quest
    resp = auth_client.get(url_for('groups.read_all_members', group_id = '1'))
    # THEN expect the same number of members
    assert len(resp.json) == count

@pytest.mark.smoke
def test_read_one_member(auth_client):
    # GIVEN an empty database
    # WHEN we add in members
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    create_multiple_members(auth_client.sqla, fraction=0.75)
    # WHEN we read the first member
    first_member = auth_client.sqla.query(Member).first()
    resp = auth_client.get(url_for('groups.read_one_member', group_id = first_member.group_id, person_id = first_member.person_id))
    # Then test both group_id and person_id
    assert first_member.group_id == resp.json['groupId']
    assert first_member.person_id == resp.json['person']['id']

@pytest.mark.smoke
def test_update_member(auth_client):
    # GIVEN an empty database
    # WHEN we add in members
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    create_multiple_members(auth_client.sqla, fraction=0.75)
    # WHEN we update the first member
    first_member = auth_client.sqla.query(Member).first()
    # THEN we expect an correct message
    resp = auth_client.patch(url_for('groups.read_one_member', group_id = first_member.group_id, person_id = first_member.person_id), json = {'active':False})
    assert resp.status_code == 200

def test_update_member_identity(auth_client):
    # GIVEN a database with person1, person2 in group1
    create_multiple_groups(auth_client.sqla, 2)
    group1, group2 = auth_client.sqla.query(Group).all()
    create_multiple_people(auth_client.sqla, 2)
    person1_id, person2_id = [ person.id for person in auth_client.sqla.query(Person).all() ]
    group1.members += [
            Member(person_id=person1_id, group_id=group1.id, joined=fake.date()),
            Member(person_id=person2_id, group_id=group1.id, joined=fake.date())
            ]
    auth_client.sqla.add(group1)
    auth_client.sqla.commit()
    # WHEN we move person1 to group2
    resp = auth_client.patch(url_for('groups.update_member', group_id=group1.id, person_id=person1_id), json = {'groupId': group2.id})
    # THEN we expect the request to succeed
    assert resp.status_code == 200
    # THEN we expect person1 to be in group2
    assert auth_client.sqla.query(Member).filter_by(group_id=group2.id, person_id=person1_id).first()
    # THEN we expect person1 not to be in group1
    assert not auth_client.sqla.query(Member).filter_by(group_id=group1.id, person_id=person1_id).first()

    # WHEN we move change group2.person1's identity to person2
    resp = auth_client.patch(url_for('groups.update_member', group_id=group2.id, person_id=person1_id), json = {'personId': person2_id})
    # THEN we expect the request to succeed
    assert resp.status_code == 200
    # THEN we expect person2 to be in group2
    assert auth_client.sqla.query(Member).filter_by(group_id=group2.id, person_id=person2_id).first()
    # THEN we expect person1 not to be in group2
    assert not auth_client.sqla.query(Member).filter_by(group_id=group2.id, person_id=person1_id).first()

    # GIVEN person2 in group1 and group2
    # WHEN we try to move person2 from group1 to group2
    resp = auth_client.patch(url_for('groups.update_member', group_id=group1.id, person_id=person2_id), json = {'groupId': group2.id})
    # THEN we expect an error code
    assert resp.status_code == 409
    # WHEN we try to move person2 to a non-existent group
    resp = auth_client.patch(url_for('groups.update_member', group_id=group1.id, person_id=person2_id), json = {'groupId': -1})
    # THEN we expect an error code
    assert resp.status_code == 404

# # ---- Attendance
@pytest.mark.smoke
def test_create_attendance(auth_client):
    # GIVEN an empty database
    # WHEN we add in attendance
    create_multiple_meetings(auth_client.sqla, random.randint(3, 6))
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    first_meeting = auth_client.sqla.query(Meeting).first()
    first_person = auth_client.sqla.query(Person).first()
    # WHEN add attendance with perosn_id and meeting_id
    resp = auth_client.post(url_for('groups.create_attendance', meeting_id = first_meeting.id, person_id = first_person.id))
    # THEN expect correct message
    assert resp.status_code == 201

    # WHEN test with 404 error
    resp = auth_client.post(url_for('groups.create_attendance', meeting_id = first_meeting.id, person_id = 99))
    # THEN expect error 404 message
    assert resp.status_code == 404

    # WHEN test with 409 error
    resp = auth_client.post(url_for('groups.create_attendance', meeting_id = first_meeting.id, person_id = first_person.id))
    resp = auth_client.post(url_for('groups.create_attendance', meeting_id = first_meeting.id, person_id = first_person.id))
    # THEN expect error 409 message
    assert resp.status_code == 409

@pytest.mark.smoke
def test_read_all_attendances(auth_client):
    # GIVEN an empty database
    # WHEN we read all attendance
    create_multiple_meetings(auth_client.sqla, random.randint(3, 6))
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    create_multiple_attendance(auth_client.sqla, fraction=0.75)
    all_attendance = auth_client.sqla.query(Attendance).all()
    first_meeting = auth_client.sqla.query(Meeting).first()
    first_person = auth_client.sqla.query(Person).first()
    # WHEN read all the peron's id and whih meeting they are at
    # THEN find the attendance in a meeting wich specific meeting id
    count = 0
    for attendance in all_attendance:
        if attendance.meeting_id == first_meeting.id:
            count+=1
    resp = auth_client.get(url_for('groups.read_all_attendances', meeting_id = first_meeting.id))
    # THEN expect the same number of attendacne
    assert len(resp.json) == count

@pytest.mark.skip
def test_read_attendance_by_member(auth_client):
    pass

@pytest.mark.skip
def test_read_attendance_by_meeting(auth_client):
    pass

@pytest.mark.smoke
def test_delete_attendance(auth_client):
    # GIVEN an empty database
    # WHEN we add in attendance
    create_multiple_meetings(auth_client.sqla, random.randint(3, 6))
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    first_meeting = auth_client.sqla.query(Meeting).first()
    first_person = auth_client.sqla.query(Person).first()
    # WHEN add attendance with perosn_id and meeting_id
    auth_client.sqla.add(Attendance(meeting_id = first_meeting.id, person_id = first_person.id))
    auth_client.sqla.commit()
    # WHEN delete the first meeting
    resp = auth_client.delete(url_for('groups.delete_attendance', meeting_id = first_meeting.id, person_id = first_person.id))
    #THEN expect correct message
    assert resp.status_code == 204

    # WHEN delete the not-exist attendance
    first_person = auth_client.sqla.query(Person).first()
    resp = auth_client.delete(url_for('groups.delete_attendance', meeting_id = first_meeting.id, person_id = first_person.id))
    # THEN expect error message
    assert resp.status_code == 404

@pytest.mark.skip
def test_repr_group(auth_client):
    pass

@pytest.mark.skip
def test_repr_meeting(auth_client):
    pass

@pytest.mark.skip
def test_repr_member(auth_client):
    pass

@pytest.mark.skip
def test_repr_attendance(auth_client):
    pass

@pytest.mark.smoke
def test_add_group_images(auth_client):
    # GIVEN a set of groups and images
    count = random.randint(3, 6)
    create_multiple_groups(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    groups = auth_client.sqla.query(Group).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN an image is requested to be tied to each group
    for i in range(count):
        print(i)
        resp = auth_client.post(url_for('groups.add_group_images', group_id=groups[i].id, image_id=images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the group to have a single image
        assert len(auth_client.sqla.query(Group).filter_by(id=groups[i].id).first().images) == 1

def test_add_group_images_no_exist(auth_client):
    # GIVEN a set of groups and images
    count = random.randint(3, 6)
    create_multiple_groups(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    groups = auth_client.sqla.query(Group).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN a no existant image is requested to be tied to an group
    resp = auth_client.post(url_for('groups.add_group_images', group_id=1, image_id=len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existant group
    resp = auth_client.post(url_for('groups.add_group_images', group_id=count + 1, image_id=1))

    # THEN expect the group not to be found
    assert resp.status_code == 404

def test_add_group_images_already_exist(auth_client):
    # GIVEN a set of groups, images, and group_image relationships
    count = random.randint(3, 6)
    create_multiple_groups(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_groups(auth_client.sqla)

    group_images = auth_client.sqla.query(ImageGroup).all()

    # WHEN existing group_image relationships are requested to be created
    for group_image in group_images:
        resp = auth_client.post(
            url_for('groups.add_group_images', group_id=group_image.group_id, image_id=group_image.image_id))

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422

@pytest.mark.smoke
def test_delete_group_image(auth_client):
    # GIVEN a set of groups, images, and group_image relationships
    count = random.randint(3, 6)
    create_multiple_groups(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_groups(auth_client.sqla)

    valid_group_image = auth_client.sqla.query(ImageGroup).first()

    # WHEN the group_image relationships are requested to be deleted
    resp = auth_client.delete(
        url_for('groups.delete_group_image', group_id=valid_group_image.group_id, image_id=valid_group_image.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204

def test_delete_group_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a group_image relationship is requested to be deleted
    resp = auth_client.delete(
        url_for('groups.delete_group_image', group_id=random.randint(1, 8), image_id=random.randint(1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404

# ---- Manager Type

@pytest.mark.smoke
def test_create_manager_type(auth_client):
    # GIVEN an empty database
    # WHEN we add in a manager type
    resp = auth_client.post(url_for('groups.create_manager_type'), json = {'name':'manager_type_1'})
    # THEN expect the create to run OK
    assert resp.status_code == 201

    # WHEN we create an invalid manager type
    resp = auth_client.post(url_for('groups.create_manager_type'), json = {'name':''})
    # THEN we expect the request to be unprocessable
    assert resp.status_code == 422

    # THEN we expect the correct number of items in the database
    assert auth_client.sqla.query(ManagerType).count() == 1

@pytest.mark.smoke
def test_read_one_manager_type(auth_client):
    # GIVEN a database with a number of manager types
    count = random.randint(3, 11)
    create_multiple_manager_types(auth_client.sqla, count)

    manager_types = auth_client.sqla.query(ManagerType).all()

    # WHEN we ask for the manager_types one by one
    for manager_type in manager_types:
        # THEN we expect each of them to correspond to the manager_type in the database
        resp = auth_client.get(
            url_for('groups.read_one_manager_type', manager_type_id=manager_type.id))
        assert resp.status_code == 200
        assert resp.json['name'] == manager_type.name

@pytest.mark.smoke
def test_read_all_manager_types(auth_client):
    # GIVEN a database with some manager_types
    count = random.randint(3, 11)
    create_multiple_manager_types(auth_client.sqla, count)

    # WHEN we read all active manager_types
    resp = auth_client.get(url_for('groups.read_all_manager_types'))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the database has the same number of manager_types as we created
    manager_types = auth_client.sqla.query(ManagerType).all()
    assert len(manager_types) == count

@pytest.mark.smoke
def test_update_manager_type(auth_client):
    # GIVEN a database with a number of manager_types
    count = random.randint(3, 11)
    create_multiple_manager_types(auth_client.sqla, count)
    # WHEN we update one manager_type
    manager_type = auth_client.sqla.query(ManagerType).first()
    payload = manager_type_object_factory("new_name")
    resp = auth_client.patch(
        url_for('groups.update_manager_type', manager_type_id=manager_type.id), json=payload)
    # THEN we assume the correct status code
    assert resp.status_code == 200
    # THEN we assume the correct content in the returned object
    assert resp.json['name'] == 'new_name'
    # THEN we assume the correct content in the database
    assert auth_client.sqla.query(ManagerType).filter_by(id=manager_type.id).first().name == 'new_name'

@pytest.mark.smoke
def test_delete_manager_type(auth_client):
    # GIVEN a database with a number of manager_types
    count = random.randint(3, 11)
    create_multiple_manager_types(auth_client.sqla, count)
    # WHEN we delete one of them
    manager_type = auth_client.sqla.query(ManagerType).first()
    resp = auth_client.delete(url_for('groups.delete_manager_type', manager_type_id = manager_type.id))
    # THEN we assume the correct status code
    assert resp.status_code == 204
    # WHEN we delete a non-existent item
    resp = auth_client.delete(url_for('groups.delete_manager_type', manager_type_id = -1))
    # THEN we expect an error
    assert resp.status_code == 404
    # THEN we assume the number of manager_types in the database to be the correct number
    manager_types = auth_client.sqla.query(ManagerType).all()
    assert len(manager_types) == count - 1

# ---- Manager: Moved from people module

@pytest.mark.smoke
def test_create_manager(auth_client):
    # GIVEN an empty database
    # WHEN we add in a manager
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    manager = auth_client.sqla.query(Manager).all()
    people = auth_client.sqla.query(Person).all()
    # WHEN we are creating a manager, we need to find the one who is not a manager
    working_person = []
    for one in manager:
        working_person.append(one.person_id)
    new_manager = None
    for available_person in range(len(people)):
        if people[available_person].id not in working_person:
            new_manager = people[available_person].id
    # Then we create a manager with the avaliable person
    resp = auth_client.post(url_for('groups.create_manager', group_id = manager[0].group_id), json = {'personId':new_manager, 'managerTypeId':'1', 'active':'True'})
    # THEN expect the create to run OK
    assert resp.status_code == 201
    # WHEN we create an invalid manager
    resp = auth_client.post(url_for('groups.create_manager', group_id = 1), json = {'personId':-1, 'managerTypeId':1, 'active':True})
    # THEN we expect the request to be unprocessable
    assert resp.status_code == 404

@pytest.mark.smoke
def test_create_exist_manager(auth_client):
    # GIVEN an empty database
    # WHEN we add in a manager
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    manager = auth_client.sqla.query(Manager).all()
    people = auth_client.sqla.query(Person).all()
    # WHEN we create an existing manager
    exist_manager = auth_client.sqla.query(Manager).first()
    resp = auth_client.post(url_for('groups.create_manager', group_id = exist_manager.group_id), json = {'personId':exist_manager.person_id, 'managerTypeId':1, 'active':True})
    assert resp.status_code == 409

@pytest.mark.smoke
def test_read_all_managers(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we read all active managers
    manager = auth_client.sqla.query(Manager).all()
    number_of_manager = len(manager)
    resp = auth_client.get(url_for('groups.create_manager', group_id = '1'))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the database has the same number of manager_types as we created
    assert number_of_manager == len(resp.json)

@pytest.mark.smoke
def test_read_one_manager(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we read an active manager
    manager = auth_client.sqla.query(Manager).first()
    resp = auth_client.get(url_for('groups.read_one_manager', group_id =manager.group_id, person_id = manager.person_id))
    assert resp.status_code == 200
    assert resp.json['personId'] == manager.person_id

def test_read_one_manager_invalid(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we read a not existing manager
    manager = auth_client.sqla.query(Manager).first()
    resp = auth_client.get(url_for('groups.read_one_manager', group_id =manager.group_id, person_id = 2020))
    # THEN we expect the request to be unprocessable
    assert resp.status_code == 404

@pytest.mark.smoke
def test_update_manager(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we get the first manager
    first_manager = auth_client.sqla.query(Manager).first()
    # WHEN we update an existing manager
    resp = auth_client.patch(
            url_for('groups.read_one_manager', group_id =first_manager.group_id, person_id =first_manager.person_id)
            , json={'active': False})
    # THEN we assume the correct status code
    assert resp.status_code == 200

def test_update_manager_invalid(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we get the first manager
    first_manager = auth_client.sqla.query(Manager).first()
    # THEN we update an invalid manager
    resp = auth_client.patch(
            url_for('groups.read_one_manager', group_id =999, person_id =first_manager.person_id)
            , json={'active': False})
    assert resp.status_code == 404

@pytest.mark.smoke
def test_delete_manager(auth_client):
    # GIVEN an empty database
    # WHEN we add in managers
    create_multiple_groups(auth_client.sqla,1)
    create_multiple_manager_types(auth_client.sqla,1)
    create_multiple_managers(auth_client.sqla, 0.75)
    # WHEN we get the first manager
    first_manager = auth_client.sqla.query(Manager).first()
    # AND we delete one of the managers
    resp = auth_client.delete(url_for('groups.delete_manager', group_id =first_manager.group_id, person_id =first_manager.person_id))
    # THEN we assume the correct status code
    assert resp.status_code == 204

@pytest.mark.skip
def test_delete_manager_no_exist(auth_client):
    pass

@pytest.mark.skip
def test_delete_manager_with_subordinate(auth_client):
    pass

@pytest.mark.skip
def test_create_manager_with_superior(auth_client):
    pass

@pytest.mark.skip
def test_repr_manager(auth_client):
    pass

def test_get_all_subgroups(auth_client):
    # GIVEN test case 1 for group hierarchy
    create_multiple_group_types(auth_client.sqla, 1)
    create_multiple_manager_types(auth_client.sqla, 1)
    create_hierarchy_test_case_1(auth_client.sqla)

    # WHEN we get the subgroups of person 1
    subgroups = get_all_subgroups(1)

    # THEN we assume the correct collection of subgroups
    assert len(subgroups) == 4
    assert 9 not in subgroups
    assert 4 in subgroups

    # WHEN we get the subgroups of person 2
    subgroups = get_all_subgroups(2)

    # THEN we assume the correct collection of subgroups
    assert len(subgroups) == 0

    # WHEN we get the subgroups of person 8
    subgroups = get_all_subgroups(8)
    # THEN we assume the correct collection of subgroups
    assert len(subgroups) == 1
    assert 9 in subgroups

# ---- Authorization
def test_authorize_group_admin(auth_client):
    # GIVEN a user with group-admin role, and a user with no role
    admin_role = Role(**RoleSchema().load(role_object_factory('role.group-admin')))
    auth_client.sqla.add(admin_role)
    auth_client.sqla.commit()

    admin_user = Person(**PersonSchema().load(person_object_factory()))
    admin_user.roles.append(admin_role)
    normal_user = Person(**PersonSchema().load(person_object_factory()))
    auth_client.sqla.add_all([admin_user, normal_user])
    auth_client.sqla.commit()

    # WHEN we make a request with the admin token
    admin_token = create_access_token(identity=admin_user.username)
    resp = auth_client.post(url_for('groups.create_group_type'),
            json={'name':'group_type_1'},
            headers={'AUTHORIZATION': f'Bearer {admin_token}'})
    # THEN we expect the right status code
    assert resp.status_code == 201

    # WHEN we make a request with the normal token
    resp = auth_client.post(url_for('groups.create_group_type'),
            json={'name':'group_type_1'})
    # THEN we expect an error
    assert resp.status_code == 403

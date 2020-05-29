import random

import pytest
from dateutil import parser
from faker import Faker
from flask import url_for

from .create_group_data import flip, create_role, group_object_factory, group_object_factory_with_members, \
    create_multiple_groups, member_object_factory, create_multiple_members, meeting_object_factory, \
    create_multiple_meetings, create_attendance, create_multiple_group_types, create_multiple_manager_types, \
    group_type_object_factory, manager_type_object_factory
from .models import Group, GroupType, Member, Meeting, MeetingSchema, Attendance, Manager, ManagerType, ManagerSchema
from ..images.create_image_data import create_images_groups
from ..images.create_image_data import create_test_images
from ..images.models import Image, ImageGroup
from ..people.test_people import create_multiple_people
from ..places.models import Address, Country
from ..places.test_places import create_multiple_addresses, create_multiple_areas

fake = Faker()


# def generate_managers(auth_client):
#     create_multiple_people(auth_client.sqla, 4)
#     # create_multiple_accounts(auth_client.sqla)
#     # create_multiple_managers(auth_client.sqla, 4, "Manager")


# ---- Group Type

@pytest.mark.smoke
def test_create_group_type(auth_client):
    # GIVEN an empty database
    # WHEN we add in a group type
    resp = auth_client.post(url_for('groups.create_group_type'), json = {'name':'group_type_1'})
    # THEN expect the create to run OK
    assert resp.status_code == 201

    # WHEN we create an invalid group type
    resp = auth_client.post(url_for('groups.create_group_type'), json = {'name':''})
    # THEN we expect the request to be unprocessable
    assert resp.status_code == 422

    # THEN we expect the correct number of items in the database
    assert auth_client.sqla.query(GroupType).count() == 1

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
# @pytest.mark.smoke
# def test_create_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_create_invalid_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_groups(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_one_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_update_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_invalid_update_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_activate_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_deactivate_group(auth_client):
#     pass
# 
# # ---- Meeting
# @pytest.mark.smoke
# def test_create_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_create_invalid_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_meetings(auth_client):
#     pass
# 
# def generate_addresses(auth_client, count=1):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_meetings_by_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_meetings_by_location(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_one_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_update_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_invalid_update_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_activate_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_deactivate_meeting(auth_client):
#     pass
# 
# # ---- Member
# @pytest.mark.smoke
# def test_create_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_members(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_one_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_update_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_activate_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_deactivate_member(auth_client):
#     pass
# 
# # ---- Attendance
# @pytest.mark.smoke
# def test_create_attendance(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_attendance(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_attendance_by_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_attendance_by_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_attendance(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_repr_group(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_repr_meeting(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_repr_member(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_repr_attendance(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_add_group_images(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_add_group_images_no_exist(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_add_group_images_already_exist(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_group_image(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_group_image_no_exist(auth_client):
#     pass



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

# @pytest.mark.smoke
# def test_create_manager(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_create_manager_invalid(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_all_managers(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_one_manager(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_read_one_manager_invalid(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_update_manager(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_update_manager_invalid(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_manager(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_manager_no_exist(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_delete_manager_with_subordinate(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_create_manager_with_superior(auth_client):
#     pass
# 
# @pytest.mark.smoke
# def test_repr_manager(auth_client):
#     pass


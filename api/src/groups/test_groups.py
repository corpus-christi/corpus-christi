import pytest
import random
import datetime
import random
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash
from dateutil import parser

from .models import Group, GroupSchema, Member, MemberSchema, Meeting, MeetingSchema, Attendance, AttendanceSchema
from .create_group_data import flip, fake, group_object_factory, create_multiple_groups, member_object_factory, create_multiple_members, meeting_object_factory, create_multiple_meetings, attendance_object_factory, create_attendance
from ..people.models import Person, Manager
from ..places.models import Address
from ..people.test_people import create_multiple_accounts, create_multiple_people, create_multiple_managers

fake = Faker()

def generate_managers(auth_client):
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_accounts(auth_client.sqla)
    create_multiple_managers(auth_client.sqla, 4, "Manager")

# ---- Group

@pytest.mark.smoke
def test_create_group(auth_client):
    # GIVEN an empty database
    generate_managers(auth_client)
    # WHEN we add in some events

    count = random.randint(5, 15)

    # WHEN
    for i in range(count):
        resp = auth_client.post(url_for('groups.create_group'), json=group_object_factory(auth_client.sqla))
        assert resp.status_code == 201

    # THEN
    assert auth_client.sqla.query(Group).count() == count


@pytest.mark.smoke
def test_create_invalid_group(auth_client):
    # GIVEN an empty database
    generate_managers(auth_client)
    # WHEN we attempt to add invalid events
    count = random.randint(5, 15)

    for i in range(count):
        group = group_object_factory(auth_client.sqla)

        if flip():
            group['name'] = None
        elif flip():
            group['description'] = None
        else:
            group['active'] = None
        group['invalid_field'] = 4

        resp = auth_client.post(url_for('groups.create_group'), json=group)

        # THEN the response should have the correct code
        assert resp.status_code == 422

    # AND the database should still be empty
    assert auth_client.sqla.query(Group).count() == 0


@pytest.mark.smoke
def test_read_all_groups(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)

    # WHEN
    resp = auth_client.get(url_for('groups.read_all_groups'))
    assert resp.status_code == 200
    groups = auth_client.sqla.query(Group).all()

    # THEN
    assert len(groups) == count
    assert len(resp.json) == count

    for i in range(count):
        assert resp.json[i]['name'] == groups[i].name


# @pytest.mark.smoke
# def test_read_all_events_with_query(auth_client):
#     # GIVEN some existing events
#     count = random.randint(3, 11)
#     create_multiple_people(auth_client.sqla, 3)
#     create_multiple_managers(auth_client.sqla, 2, "Manager")
#     create_multiple_groups(auth_client.sqla, count)
#     all_groups = auth_client.sqla.query(Group).all()
#
#     for _ in range(15):
#         # WHEN queried for all events matching a flag
#         query_string = dict()
#         if flip():
#             query_string['return_group'] = 'inactive'
#         else:
#             query_string['return_group'] = 'both'
#
#         if flip():
#             query_string['start'] = datetime.datetime.now().strftime('%Y-%m-%d')
#         if flip():
#             query_string['end'] = datetime.datetime.now().strftime('%Y-%m-%d')
#
#         if flip():
#             query_string['title'] = 'c'
#
#         if flip():
#             query_string['location_id'] = 1
#
#         if flip():
#             query_string['include_assets'] = 1
#
#         # THEN the response should match those flags
#         resp = auth_client.get(url_for('events.read_all_events'), query_string=query_string)
#         assert resp.status_code == 200
#         events = auth_client.sqla.query(Event).all()
#
#         for event in resp.json:
#             if 'return_group' in query_string:
#                 if query_string['return_group'] == 'inactive':
#                     assert event['active'] == False
#             else:
#                 assert event['active'] == True
#
#             if 'start' in query_string:
#                 assert datetime.datetime.strptime(event['start'][:event['start'].index('T')],
#                                                   '%Y-%m-%d') >= datetime.datetime.strptime(query_string['start'],
#                                                                                             '%Y-%m-%d')
#             if 'end' in query_string:
#                 assert datetime.datetime.strptime(event['end'][:event['end'].index('T')],
#                                                   '%Y-%m-%d') <= datetime.datetime.strptime(query_string['end'],
#                                                                                             '%Y-%m-%d')
#
#             if 'title' in query_string:
#                 assert query_string['title'].lower() in event['title'].lower()
#
#             if 'location_id' in query_string:
#                 assert event['location_id'] == query_string['location_id']



@pytest.mark.smoke
def test_read_one_group(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)

    # WHEN
    groups = auth_client.sqla.query(Group).all()

    for group in groups:
        resp = auth_client.get(url_for('groups.read_one_group', group_id=group.id))
    #THEN expect groups to match
        assert resp.status_code == 200
        assert resp.json['name'] == group.name


# Not in API yet
# @pytest.mark.smoke
# def test_replace_group(auth_client):
#     # GIVEN a database with a number of groups
#     count = random.randint(3, 11)
#     create_multiple_people(auth_client.sqla, 3)
#     create_multiple_managers(auth_client.sqla, 2, "Manager")
#     create_multiple_groups(auth_client.sqla, count)
#     # WHEN we replace one event with a predefined content
#     group = auth_client.sqla.query(Group).first()
#     new_group = {
#         'name': fake.word(),
#         'start': str(fake.future_datetime(end_date="+6h")),
#         'end': str(fake.date_time_between(start_date="+6h", end_date="+1d", tzinfo=None)),
#         'active': flip()
#     }
#     resp = auth_client.put(url_for('events.replace_event', event_id=event.id), json=new_event)
#     # THEN we expect the right status code
#     assert resp.status_code == 200
#     # THEN we expect the event in the database to have the same content of the predefined content
#     assert resp.json['id'] == event.id
#     assert resp.json['title'] == new_event['title']
#     assert resp.json['active'] == new_event['active']


@pytest.mark.smoke
def test_update_group(auth_client):
    # GIVEN a database with a number of groups
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)

    # WHEN we update one group
    group = auth_client.sqla.query(Group).first()
    manager_id = auth_client.sqla.query(Manager.id).first()[0]

    payload = group_object_factory(auth_client.sqla)

    # payload['name'] = new_group['name']
    # payload['description'] = new_group['description']
    payload['manager_id'] = manager_id
    flips = flip()
    if flips:
        payload['active'] = flip()

    resp = auth_client.patch(url_for('groups.update_group', group_id=group.id), json=payload)

    # THEN we assume the correct status code
    assert resp.status_code == 201

    # THEN we assume the correct content in the returned object
    assert resp.json['name'] == payload['name']
    assert resp.json['description'] == payload['description']
    if flips:
        assert resp.json['active'] == payload['active']

# Waiting on API
# @pytest.mark.xfail()
# def test_delete_group(auth_client):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False


# ---- Meeting


@pytest.mark.smoke
def test_create_meeting(auth_client):
    # GIVEN an empty database
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 1)
    # WHEN we add in some events

    count = random.randint(5, 15)

    # WHEN
    for i in range(count):
        resp = auth_client.post(url_for('groups.create_meeting'), json=meeting_object_factory(auth_client.sqla))
        assert resp.status_code == 201

    # THEN
    assert auth_client.sqla.query(Meeting).count() == count


@pytest.mark.smoke
def test_read_all_meetings(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)
    create_multiple_meetings(auth_client.sqla, count)

    # WHEN
    resp = auth_client.get(url_for('groups.read_all_meetings'))
    assert resp.status_code == 200
    meetings = auth_client.sqla.query(Meeting).all()

    # THEN
    assert len(meetings) == count
    assert len(resp.json) == count

    for i in range(count):
        assert resp.json[i]['id'] == meetings[i].id


@pytest.mark.smoke
def test_read_one_meeting(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)
    create_multiple_meetings(auth_client.sqla, count)

    # WHEN
    meetings = auth_client.sqla.query(Meeting).all()

    for meeting in meetings:
        resp = auth_client.get(url_for('groups.read_one_meeting', meeting_id=meeting.id))
        # THEN expect groups to match
        assert resp.status_code == 200
        assert resp.json['id'] == meeting.id


# Waiting for API
# @pytest.mark.smoke
# def test_replace_meeting(auth_client):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False


@pytest.mark.smoke
def test_update_meeting(auth_client):
    # GIVEN a database with a number of meetings
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)
    create_multiple_meetings(auth_client.sqla, count)

    # WHEN we update one event
    meeting = auth_client.sqla.query(Meeting).first()

    payload = {}
    new_meeting = meeting_object_factory(auth_client.sqla)

    payload['group_id'] = new_meeting['group_id']
    payload['when'] = new_meeting['when']

    resp = auth_client.patch(url_for('groups.update_meeting', meeting_id=meeting.id), json=payload)

    # THEN we assume the correct status code
    assert resp.status_code == 200

    # THEN we assume the correct content in the returned object
    assert resp.json['group_id'] == payload['group_id']
    assert parser.parse(resp.json['when']).replace(tzinfo=None) == parser.parse(payload['when']).replace(tzinfo=None)


# Waiting for API
# @pytest.mark.xfail()
# def test_delete_meeting(auth_client, db):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False


# ---- Member


@pytest.mark.smoke
def test_create_member(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 2)

    # WHEN
    for i in range(count):
        resp = auth_client.post(url_for('groups.create_member'), json=member_object_factory(auth_client.sqla))
        assert resp.status_code == 201

    # THEN
    assert auth_client.sqla.query(Member).count() == count


@pytest.mark.smoke
def test_read_all_members(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 2)
    create_multiple_members(auth_client.sqla, count)

    # WHEN
    resp = auth_client.get(url_for('groups.read_all_members'))
    assert resp.status_code == 200
    members = auth_client.sqla.query(Member).all()

    # THEN
    assert len(members) == count
    assert len(resp.json) == count

    for i in range(count):
        assert resp.json[i]['id'] == members[i].id


@pytest.mark.smoke
def test_read_one_member(auth_client):
    # GIVEN
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)
    create_multiple_meetings(auth_client.sqla, count)

    # WHEN
    members = auth_client.sqla.query(Member).all()

    for member in members:
        resp = auth_client.get(url_for('groups.read_one_member', member_id=member.id))
        # THEN expect groups to match
        assert resp.status_code == 200
        assert resp.json['id'] == member.id

# Waiting for API
# @pytest.mark.xfail()
# def test_replace_member(auth_client, db):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False


@pytest.mark.smoke
def test_update_member(auth_client):
    # GIVEN a database with a number of meetings
    count = random.randint(3, 11)
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, count)
    create_multiple_members(auth_client.sqla, count)

    # WHEN we update one event
    member = auth_client.sqla.query(Member).first()

    payload = {}
    new_member = member_object_factory(auth_client.sqla)

    payload['group_id'] = new_member['group_id']
    payload['person_id'] = new_member['person_id']
    payload['joined'] = new_member['joined']
    payload['active'] = new_member['active']

    resp = auth_client.patch(url_for('groups.update_member', member_id=member.id), json=payload)

    # THEN we assume the correct status code
    assert resp.status_code == 200

    # THEN we assume the correct content in the returned object
    assert resp.json['group_id'] == payload['group_id']
    assert resp.json['person_id'] == payload['person_id']
    assert resp.json['joined'] == payload['joined']
    assert resp.json['active'] == payload['active']


# Waiting for API
# @pytest.mark.smoke
# def test_delete_member(auth_client):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False


# ---- Attendance


@pytest.mark.smoke
def test_create_attendance(auth_client):
    # GIVEN a database with some members and meetings
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 4)
    count_meetings = random.randint(15, 20)
    count_members = random.randint(3, 5)
    create_multiple_meetings(auth_client.sqla, count_meetings)
    create_multiple_members(auth_client.sqla, count_members)
    # WHEN we create a meeting to a member
    meeting_id = auth_client.sqla.query(Meeting.id).first()[0]
    member_id = auth_client.sqla.query(Meeting.id).first()[0]
    payload = {
            'member_id': member_id,
            'meeting_id': meeting_id
    }
    resp = auth_client.post(url_for('groups.create_attendance'), json=payload)
    # THEN we expect the right status code
    assert resp.status_code == 201
    # THEN we expect the entry to be created
    queried_attendance_count = auth_client.sqla.query(Attendance).filter(Attendance.meeting_id == payload['meeting_id'], Attendance.member_id == payload['member_id']).count()
    assert queried_attendance_count == 1

    # WHEN we create an invalid meeting
    invalid_payload = {
            'member_id': member_id,
            'meeting_id': meeting_id,
            'invalid_field': 23
    }
    resp = auth_client.post(url_for('groups.create_attendance'), json=invalid_payload)
    # THEN we expect an error
    assert resp.status_code == 422

    # to be implemented
    # # WHEN we create an existing attendance
    # resp = auth_client.post(url_for('groups.create_attendance'), json=payload)
    # # THEN we expect an error
    # assert resp.status_code == 422




@pytest.mark.smoke
def test_read_all_attendance(auth_client):
    # GIVEN a database with some attendances
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 4)
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_members(auth_client.sqla, 4)
    create_multiple_meetings(auth_client.sqla, 4)
    create_attendance(auth_client.sqla, 0.75)
    attendances_count = auth_client.sqla.query(Attendance).count()
    # WHEN reading all of them
    resp = auth_client.get(url_for('groups.read_all_attendance'))
    # THEN we should get the correct code
    assert resp.status_code == 200
    # THEN we should get the correct count
    assert len(resp.json) == attendances_count
    # THEN each one of them should correspond to something in the database
    for attendance in resp.json:
        assert auth_client.sqla.query(Attendance).filter( \
                Attendance.member_id == attendance['member_id'], \
                Attendance.meeting_id == attendance['meeting_id'], \
                ).count() == 1
        


def test_read_attendance_by_member(auth_client):
    # GIVEN a database with some attendances
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 4)
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_members(auth_client.sqla, 4)
    create_multiple_meetings(auth_client.sqla, 4)
    create_attendance(auth_client.sqla, 0.75)
    # WHEN we read attendances by member id
    member_id = auth_client.sqla.query(Member.id).first()[0]
    queried_attendance_count = auth_client.sqla.query(Attendance).filter_by(member_id=member_id).count()
    resp = auth_client.get(url_for('groups.read_attendance_by_member', member_id=member_id))
    # THEN we should get the correct code
    assert resp.status_code == 200
    # THEN the content returned should have the same length
    assert queried_attendance_count == len(resp.json)
    # THEN each of the attendance should correspond to one in the database
    for attendance in resp.json:
        assert 1 == auth_client.sqla.query(Attendance).filter_by(member_id=attendance["member_id"], meeting_id=attendance["meeting_id"]).count()

def test_read_attendance_by_meeting(auth_client):
    # GIVEN a database with some attendances
    generate_managers(auth_client)
    create_multiple_groups(auth_client.sqla, 4)
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_meetings(auth_client.sqla, 4)
    create_multiple_members(auth_client.sqla, 4)
    create_attendance(auth_client.sqla, 0.75)
    # WHEN we read attendances by meeting id
    meeting_id = auth_client.sqla.query(Meeting.id).first()[0]
    queried_attendance_count = auth_client.sqla.query(Attendance).filter_by(meeting_id=meeting_id).count()
    resp = auth_client.get(url_for('groups.read_attendance_by_meeting', meeting_id=meeting_id))
    # THEN we should get the correct code
    assert resp.status_code == 200
    # THEN the content returned should have the same length
    assert queried_attendance_count == len(resp.json)
    # THEN each of the attendance should correspond to one in the database
    for attendance in resp.json:
        assert 1 == auth_client.sqla.query(Attendance).filter_by(meeting_id=attendance["meeting_id"], member_id=attendance["member_id"]).count()



@pytest.mark.xfail()
def test_replace_attendance(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_attendance(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_attendance(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False

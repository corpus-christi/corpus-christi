import math
import random

from faker import Faker

from ..places.models import Address
from ..people.models import Person, Manager, Role, RoleSchema
from ..groups.models import Group, Meeting, Attendance, Member, GroupSchema, MeetingSchema, AttendanceSchema, MemberSchema
from ..events.models import EventGroup, EventGroupSchema, Event
from ..places.test_places import create_multiple_addresses
from ..people.test_people import create_multiple_managers, create_multiple_people


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


def group_object_factory(sqla):
    """Cook up a fake group."""
    all_managers = sqla.query(Manager).all()
    if not all_managers:
        create_multiple_managers(sqla, random.randint(3, 6))
        all_managers = sqla.query(Manager).all()
    group = {
        'name': rl_fake().word(),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip(),
        'manager_id': all_managers[random.randint(0, len(all_managers)-1)].id
    }
    return group


def group_object_factory_with_members(sqla, fraction=0.75):
    """Cook up a fake group."""
    all_managers = sqla.query(Manager).all()
    if not all_managers:
        create_multiple_managers(sqla, random.randint(3, 6))
        all_managers = sqla.query(Manager).all()
    all_people = sqla.query(Person).all()
    if not all_people:
        create_multiple_people(sqla, random.randint(3, 6))
        all_people = sqla.query(Person).all()
    group = {
        'name': rl_fake().word(),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip(),
        'manager_id': all_managers[random.randint(0, len(all_managers)-1)].id,
    }
    all_person_ids = [member.id for member in all_people]
    group['person_ids'] = random.sample(
        all_person_ids, math.floor(len(all_person_ids) * fraction))
    return group


def meeting_object_factory(sqla):
    """Cook up a fake meeting."""
    all_groups = sqla.query(Group).all()
    if not all_groups:
        create_multiple_groups(sqla, random.randint(3, 6))
        all_groups = sqla.query(Group).all()
    all_addresses = sqla.query(Address).all()
    if not all_addresses:
        create_multiple_addresses(sqla, random.randint(3, 6))
        all_addresses = sqla.query(Address).all()
    meeting = {
        'when': str(rl_fake().future_datetime(end_date="+6h")),
        'group_id': all_groups[random.randint(0, len(all_groups)-1)].id,
        'active': flip(),
        'address_id': all_addresses[random.randint(0, len(all_addresses) - 1)].id
    }
    if len(all_addresses) > 0:
        meeting["address_id"] = all_addresses[random.randint(
            0, len(all_addresses) - 1)].id

    return meeting


def member_object_factory(sqla):
    """Cook up a fake member."""
    all_groups = sqla.query(Group).all()
    if not all_groups:
        create_multiple_groups(sqla, random.randint(3, 6))
        all_groups = sqla.query(Group).all()
    all_people = sqla.query(Person).all()
    if not all_people:
        create_multiple_people(sqla, random.randint(3, 6))
        all_people = sqla.query(Person).all()
    member = {
        'joined': str(rl_fake().future_date(end_date="+6d")),
        'active': flip(),
        'group_id': all_groups[random.randint(0, len(all_groups)-1)].id,
        'person_id': all_people[random.randint(0, len(all_people)-1)].id
    }
    return member


def attendance_object_factory(meeting_id, member_id):
    """Cook up a fake attendance json object from given ids."""
    attendance = {
        'meeting_id': meeting_id,
        'member_id': member_id
    }
    return attendance


def role_object_factory(role_name):
    """Cook up a fake role."""
    role = {
        'nameI18n': role_name,
        'active': 1
    }
    return role

def event_groups_object_factory(event_id, group_id):
    """Cook up a fake eventteam json object from given ids."""
    eventgroup = {
        'event_id': event_id,
        'group_id': group_id,
        'active': flip()
    }
    return eventgroup

# ---------End of Factories


def create_multiple_groups(sqla, n):
    """Commit `n` new groups to the database. Return their IDs."""
    all_managers = sqla.query(Manager).all()
    if not all_managers:
        create_multiple_managers(sqla, random.randint(3, 6))
        all_managers = sqla.query(Manager).all()
    group_schema = GroupSchema()
    new_groups = []
    for i in range(n):
        valid_group = group_schema.load(group_object_factory(sqla))
        new_groups.append(Group(**valid_group))
    sqla.add_all(new_groups)
    sqla.commit()


def create_multiple_meetings(sqla, n):
    """Commit `n` new meetings to the database. Return their IDs."""
    meeting_schema = MeetingSchema()
    new_meetings = []
    for i in range(n):
        valid_meeting = meeting_schema.load(meeting_object_factory(sqla))
        new_meetings.append(Meeting(**valid_meeting))
    sqla.add_all(new_meetings)
    sqla.commit()


def create_multiple_members(sqla, n):
    """Commit `n` new members to the database. Return their IDs."""
    member_schema = MemberSchema()
    all_managers = sqla.query(Manager).all()
    if not all_managers:
        create_multiple_managers(sqla, random.randint(3, 6))
        all_managers = sqla.query(Manager).all()
    if not sqla.query(Group).all():
        create_multiple_groups(sqla, random.randint(3, 6))
    new_members = []
    for i in range(n):
        valid_member = member_schema.load(member_object_factory(sqla))
        member = Member(**valid_member)
        # Don't put someone in a group they are already in
        group = sqla.query(Group).filter_by(id=member.group_id).first()
        person_ids = []
        for group_member in group.members:
            person_ids.append(group_member.person_id)

        if member.person_id not in person_ids:
            new_members.append(Member(**valid_member))
            sqla.add(member)
            sqla.commit()


def create_attendance(sqla, fraction=0.75):
    """Create data for attendance with member/meeting"""
    attendance_schema = AttendanceSchema()
    new_attendances = []
    if not sqla.query(Member).all():
        create_multiple_people(sqla, random.randint(3, 6))
    if not sqla.query(Meeting).all():
        create_multiple_meetings(sqla, random.randint(3, 6))
    all_attendances = sqla.query(Member, Meeting).all()
    sample_attendances = random.sample(
        all_attendances, math.floor(len(all_attendances) * fraction))
    for attendance in sample_attendances:
        meeting_id = attendance[1].id
        member_id = attendance[0].id
        valid_attendance = attendance_schema.load(
            attendance_object_factory(meeting_id, member_id))
        new_attendances.append(Attendance(**valid_attendance))
    sqla.add_all(new_attendances)
    sqla.commit()


def create_role(sqla):
    """Commit new role to the database. Return ID."""
    role_schema = RoleSchema()

    valid_role_object = role_schema.load(role_object_factory(
        "role.group-overseer"))  # fake role is fake job
    valid_role_row = Role(**valid_role_object)
    sqla.add(valid_role_row)
    sqla.commit()
    return valid_role_row.id


def create_group_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_groups(sqla, 18)
    create_multiple_meetings(sqla, 12)
    create_multiple_members(sqla, 13)
    create_attendance(sqla, 0.75)
    create_events_groups(sqla, 0.75)


def create_events_groups(sqla, fraction=0.75):
    """Create data in the link table between events and groups"""
    event_groups_schema = EventGroupSchema()
    new_events_groups = []
    all_events_groups = sqla.query(Event, Group).all()
    sample_events_groups = random.sample(all_events_groups, math.floor(len(all_events_groups) * fraction))
    for events_groups in sample_events_groups:
        valid_events_groups = event_groups_schema.load(event_groups_object_factory(events_groups[0].id,events_groups[1].id))
        new_events_groups.append(EventGroup(**valid_events_groups))
    sqla.add_all(new_events_groups)
    sqla.commit()

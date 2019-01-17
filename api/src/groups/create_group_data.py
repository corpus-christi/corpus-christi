import math
import random

from faker import Faker

from ..places.models import Address
from ..people.models import Person, Manager
from ..groups.models import Group, Meeting, Attendance, Member, GroupSchema, MeetingSchema, AttendanceSchema, MemberSchema


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
    group = {
        'name': rl_fake().word(),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip(),
        'manager_id': all_managers[random.randint(0, len(all_managers)-1)].id
    }
    return group


def meeting_object_factory(sqla):
    """Cook up a fake meeting."""
    all_groups = sqla.query(Group).all()
    all_addresses = sqla.query(Address).all()
    meeting = {
        'when': str(rl_fake().future_datetime(end_date="+6h")),
        'group_id': all_groups[random.randint(0, len(all_groups)-1)].id,
        'address_id': all_addresses[random.randint(0, len(all_addresses)-1)].id
    }
    return meeting


def member_object_factory(sqla):
    """Cook up a fake member."""
    all_groups = sqla.query(Group).all()
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


#---------End of Factories


def create_multiple_groups(sqla, n):
    """Commit `n` new groups to the database. Return their IDs."""
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
    new_members= []
    for i in range(n):
        valid_member = member_schema.load(member_object_factory(sqla))
        new_members.append(Member(**valid_member))
    sqla.add_all(new_members)
    sqla.commit()

def create_attendance(sqla, fraction=0.75):
    """Create data for attendance with member/meeting"""
    attendance_schema = AttendanceSchema()
    new_attendances = []
    all_attendances = sqla.query(Member, Meeting).all()
    sample_attendances = random.sample(all_attendances, math.floor(len(all_attendances) * fraction))
    for attendance in sample_attendances:
        valid_attendance = attendance_schema.load(attendance_object_factory(attendance[0].id,attendance[1].id))
        new_attendances.append(Attendance(**valid_attendance))
    sqla.add_all(new_attendances)
    sqla.commit()


def create_group_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_groups(sqla, 18)
    create_multiple_meetings(sqla, 12)
    create_multiple_members(sqla, 13)
    create_attendance(sqla, 0.75)

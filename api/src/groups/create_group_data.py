import datetime
import math
import random

from faker import Faker

from ..events.models import EventGroup, EventGroupSchema, Event
from ..groups.models import Manager, ManagerType, Group, GroupType, Meeting, Attendance, Member, ManagerSchema, GroupSchema, MeetingSchema, AttendanceSchema, MemberSchema, GroupTypeSchema, ManagerTypeSchema
from ..people.models import Person, Role, RoleSchema
from ..people.test_people import create_multiple_people
from ..places.models import Address
from ..places.test_places import create_multiple_addresses



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


def group_object_factory(group_type_id):
    """Cook up a fake group."""
    group = {
        'name': rl_fake().word(),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip(),
        'groupTypeId': group_type_id
    }
    return group


def meeting_object_factory(group_id, address_id):
    """Cook up a fake meeting."""
    meeting = {
            'description': rl_fake().sentence(),
            'active': flip(),
            'groupId': group_id,
            'addressId': address_id,
            'startTime': str(rl_fake().future_datetime()),
            'stopTime': str(rl_fake().future_datetime()),
            }
    return meeting

def member_object_factory(person_id, group_id, active=True, joined=datetime.date.today()):
    """Cook up a fake member."""
    member = {
            'personId': person_id,
            'groupId': group_id,
            'active': active,
            'joined': joined
            }
    return member

def manager_object_factory(person_id, group_id, manager_type_id, active=True):
    """Cook up a fake manager."""
    manager = {
            'personId': person_id,
            'groupId': group_id,
            'managerTypeId': manager_type_id,
            'active': active,
            }
    return manager

def attendance_object_factory(meeting_id, person_id):
    """Cook up a fake attendance json object from given ids."""
    attendance = {
        'meetingId': meeting_id,
        'personId': person_id
    }
    return attendance

def group_type_object_factory(group_type_name):
    """Cook up a fake group type """
    group_type = {
        'name': group_type_name
    }
    return group_type

def manager_type_object_factory(manager_type_name):
    """Cook up a fake manager type """
    manager_type = {
        'name': manager_type_name
    }
    return manager_type


# ---------End of Factories


def create_multiple_groups(sqla, n):
    """Commit `n` new groups to the database. Return their IDs."""
    group_schema = GroupSchema()
    new_groups = []
    group_type = sqla.query(GroupType).first()
    if group_type is None:
        create_multiple_group_types(sqla, 1)
        group_type = sqla.query(GroupType).first()
    for i in range(n):
        valid_group = group_schema.load(group_object_factory(group_type.id))
        new_groups.append(Group(**valid_group))
    sqla.add_all(new_groups)
    sqla.commit()


def create_multiple_meetings(sqla, n):
    """Commit `n` new meetings to the database. Return their IDs."""
    meeting_schema = MeetingSchema()
    new_meetings = []
    if sqla.query(Group).count() == 0:
        create_multiple_groups(sqla, random.randint(3, 6))
    all_groups = sqla.query(Group).all()

    if sqla.query(Address).count() == 0:
        create_multiple_addresses(sqla, random.randint(3, 6))
    all_addresses = sqla.query(Address).all()

    for i in range(n):
        valid_meeting = meeting_schema.load(meeting_object_factory(
            group_id=random.choice(all_groups).id,
            address_id=random.choice(all_addresses).id,
            ))
        new_meetings.append(Meeting(**valid_meeting))
    sqla.add_all(new_meetings)
    sqla.commit()


def create_multiple_members(sqla, fraction=0.75):
    # set up environment for creating members
    member_schema = MemberSchema()
    if sqla.query(Group).count() == 0:
        create_multiple_groups(sqla, random.randint(3, 6))
    all_groups = sqla.query(Group).all()
    if sqla.query(Person).count() == 0:
        create_multiple_people(sqla, random.randint(3, 6))

    # TODO: query from non-existing members, so that multiple calls won't fail <2020-06-02, David Deng> #
    all_members = sqla.query(Person, Group).all()
    sample_members = random.sample(
            all_members, math.floor(len(all_members) * fraction))

    new_members = []
    for person, group in sample_members:
        valid_member = member_schema.load(member_object_factory(
            person.id, group.id, active=flip(), joined=fake.date()))
        new_members.append(Member(**valid_member))
    sqla.add_all(new_members)
    sqla.commit()

def create_multiple_managers(sqla, fraction=0.75):
    """Commit `n` new managers to the database """
    # set up environment for creating managers
    manager_schema = ManagerSchema()
    if sqla.query(ManagerType).count() == 0:
        create_multiple_manager_types(sqla, random.randint(3, 6))
    all_manager_types = sqla.query(ManagerType).all()
    if sqla.query(Group).count() == 0:
        create_multiple_groups(sqla, random.randint(3, 6))
    all_groups = sqla.query(Group).all()
    if sqla.query(Person).count() == 0:
        create_multiple_people(sqla, random.randint(3, 6))

    all_managers = sqla.query(Person, Group).all()
    sample_managers = random.sample(
            all_managers, math.floor(len(all_managers) * fraction))

    new_managers = []
    for person, group in sample_managers:
        manager_type_id = random.choice(all_manager_types).id
        valid_manager = manager_schema.load(manager_object_factory(person.id, group.id, manager_type_id))
        new_managers.append(Manager(**valid_manager))
    sqla.add_all(new_managers)
    sqla.commit()


def create_multiple_attendance(sqla, fraction=0.75):
    """Create data for attendance with member/meeting"""
    attendance_schema = AttendanceSchema()
    new_attendances = []
    if not sqla.query(Member).all():
        create_multiple_people(sqla, random.randint(3, 6))
    if not sqla.query(Meeting).all():
        create_multiple_meetings(sqla, random.randint(3, 6))
    all_attendances = sqla.query(Person, Meeting).all()
    sample_attendances = random.sample(
        all_attendances, math.floor(len(all_attendances) * fraction))
    for attendance in sample_attendances:
        meeting_id = attendance[1].id
        person_id = attendance[0].id
        valid_attendance = attendance_schema.load(
            attendance_object_factory(meeting_id, person_id))
        new_attendances.append(Attendance(**valid_attendance))
    sqla.add_all(new_attendances)
    sqla.commit()


def create_multiple_group_types(sqla, n):
    """Commit `n` new group types to the database."""
    group_type_schema = GroupTypeSchema()
    new_group_types = []
    for i in range(n):
        valid_group_type = group_type_schema.load(group_type_object_factory(" ".join(fake.words(2))))
        new_group_types.append(GroupType(**valid_group_type))
    sqla.add_all(new_group_types)
    sqla.commit()

def create_multiple_manager_types(sqla, n):
    """Commit `n` new manager types to the database."""
    manager_type_schema = ManagerTypeSchema()
    new_manager_types = []
    for i in range(n):
        valid_manager_type = manager_type_schema.load(manager_type_object_factory(" ".join(fake.words(2))))
        new_manager_types.append(ManagerType(**valid_manager_type))
    sqla.add_all(new_manager_types)
    sqla.commit()


def create_group_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_group_types(sqla, 5)
    create_multiple_manager_types(sqla, 5)
    create_multiple_groups(sqla, 4)
    create_multiple_managers(sqla, 0.75)
    create_multiple_members(sqla, 0.75)
    create_multiple_meetings(sqla, 12)
    create_multiple_attendance(sqla, 0.75)


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
        'groupId': all_groups[random.randint(0, len(all_groups) - 1)].id,
        'addressId': all_addresses[random.randint(0, len(all_addresses) - 1)].id,
        'startTime': str(rl_fake().future_datetime(end_date=f'+{random.randint(3,6)}h')),
        'stopTime': str(rl_fake().future_datetime(end_date=f'+{random.randint(7, 20)}h')),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip()
    }
    if len(all_addresses) > 0:
        meeting["addressId"] = all_addresses[random.randint(
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
        'groupId': all_groups[random.randint(0, len(all_groups) - 1)].id,
        'personId': all_people[random.randint(0, len(all_people) - 1)].id
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

def attendance_object_factory(meeting_id, member_id):
    """Cook up a fake attendance json object from given ids."""
    attendance = {
        'meetingId': meeting_id,
        'memberId': member_id
    }
    return attendance

def role_object_factory(role_name):
    """Cook up a fake role."""
    role = {
        'nameI18n': role_name,
        'active': 1
    }
    return role

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
    for i in range(n):
        valid_meeting = meeting_schema.load(meeting_object_factory(sqla))
        new_meetings.append(Meeting(**valid_meeting))
    sqla.add_all(new_meetings)
    sqla.commit()


def create_multiple_members(sqla, n):
    """Commit `n` new members to the database. Return their IDs."""
    member_schema = MemberSchema()
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
    # group_person_ids = [ (manager.group_id, manager.person_id) 
    #         for manager in sqla.query(Manager).all() ]
    for person, group in sample_managers:
        # generating non-existing group_id, person_id pair
        # group_id = random.choice(all_groups).id
        # person_id = random.choice(all_persons).id
        #     if (group_id, person_id) not in group_person_ids:
        #         group_person_ids.append((group_id, person_id))
        #         break
        manager_type_id = random.choice(all_manager_types).id
        valid_manager = manager_schema.load(manager_object_factory(person.id, group.id, manager_type_id))
        new_managers.append(Manager(**valid_manager))
    sqla.add_all(new_managers)
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
    create_multiple_managers(sqla, 20)
    # create_multiple_meetings(sqla, 12)
    # create_multiple_members(sqla, 13)
    # create_attendance(sqla, 0.75)


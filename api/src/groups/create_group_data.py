import datetime
import math
import random

from faker import Faker

from ..events.models import EventGroup, EventGroupSchema, Event
from ..groups.models import Manager, ManagerType, Group, GroupType, Meeting, Attendance, Member, ManagerSchema, GroupSchema, MeetingSchema, AttendanceSchema, MemberSchema, GroupTypeSchema, ManagerTypeSchema, MemberHistory, MemberHistorySchema
from ..people.models import Person, Role, RoleSchema, PersonSchema
from ..people.test_people import create_multiple_people, person_object_factory
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


def group_object_factory(group_type_id, **attributes):
    """Cook up a fake group."""
    group = {
        'name': rl_fake().word(),
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip(),
        'groupTypeId': group_type_id,
        **attributes
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


def member_object_factory(
        person_id, group_id, active=True, joined=fake.date()):
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


def member_history_object_factory(
        person_id,
        group_id,
        joined=None,
        left=None):
    """Cook up a fake member history """
    member_history = {
        'personId': person_id,
        'groupId': group_id,
        'joined': joined or str(fake.date_between(start_date='-3y', end_date='today')),
        'left': left or str(datetime.date.today())
    }
    return member_history


# ---------End of Factories


def create_multiple_groups(sqla, n):
    """Commit `n` new groups to the database. Return their IDs."""
    group_schema = GroupSchema()

    group_types = sqla.query(GroupType).all()
    if len(group_types) == 0:
        create_multiple_group_types(sqla, 3)
        group_types = sqla.query(GroupType).all()

    group_name_samples = [
        "Celebrate Recovery",
        "Illness Support",
        "Financial Peace",
        "Divorce Care",
        "Grief Share",
        "Single and Solo Moms",
        "Venezuelan Refugee Support",
        "Iron Man - Men's Group",
        "New Christians",
        "Highschool Connect",
        "Married With Kids",
        "Women of Faith",
        "Service Project",
        "Praying for Todays Issues",
        "Discovering Your Gifts"
    ]
    group_names = group_name_samples[:n]
    new_groups = [
        Group(
            **group_schema.load(
                group_object_factory(
                    random.choice(group_types).id,
                    name=name))) for name in group_names]
    for _ in range(n - len(group_name_samples)):
        new_groups.append(
            Group(**group_schema.load(group_object_factory(random.choice(group_types).id))))

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

    # TODO: query from non-existing members, so that multiple calls won't fail
    # <2020-06-02, David Deng> #
    all_members = sqla.query(Person, Group).all()
    sample_members = random.sample(
        all_members, math.floor(len(all_members) * fraction))

    new_members = []
    for person, group in sample_members:
        valid_member = member_schema.load(
            member_object_factory(person.id, group.id))
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
        valid_manager = manager_schema.load(
            manager_object_factory(
                person.id, group.id, manager_type_id))
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
    group_type_samples = [
        'Bible Study',
        'Service Projects',
        'Worship',
        'Logistics',
        'Event Planning']
    if n <= len(group_type_samples):
        group_type_names = group_type_samples[:n]
    else:
        group_type_names = group_type_samples
        for i in range(n - len(group_type_samples)):
            group_type_names.append(" ".join(fake.words(2) + ['Team']))
    new_group_types = [GroupType(
        **group_type_schema.load(group_type_object_factory(name))) for name in group_type_names]
    sqla.add_all(new_group_types)
    sqla.commit()


def create_multiple_manager_types(sqla, n):
    """Commit `n` new manager types to the database."""
    manager_type_schema = ManagerTypeSchema()
    new_manager_types = []
    for i in range(n):
        valid_manager_type = manager_type_schema.load(
            manager_type_object_factory(" ".join(fake.words(2))))
        new_manager_types.append(ManagerType(**valid_manager_type))
    sqla.add_all(new_manager_types)
    sqla.commit()


def create_multiple_member_histories(sqla, n):
    member_history_schema = MemberHistorySchema()
    if sqla.query(Group).count() == 0:
        create_multiple_groups(sqla, random.randint(3, 6))
    all_groups = sqla.query(Group).all()
    if sqla.query(Person).count() == 0:
        create_multiple_people(sqla, random.randint(3, 6))
    all_persons = sqla.query(Person).all()

    new_member_histories = []
    for i in range(n):
        group_id = random.choice(all_groups).id
        person_id = random.choice(all_persons).id
        valid_member_history = member_history_schema.load(
            member_history_object_factory(person_id, group_id))
        new_member_histories.append(MemberHistory(**valid_member_history))
    sqla.add_all(new_member_histories)
    sqla.commit()


def create_hierarchical_groups_and_participants(
        sqla, group_members, group_managers):
    """Create hardcoded groups and members and managers that represents a valid
    leadership hierarchy. Assumes existing group types and manager types both
    group_members and group_managers are lists of two-element tuples in the
    form of [group_id, person_id].
    """

    group_type_id = sqla.query(GroupType).first().id
    manager_type_id = sqla.query(ManagerType).first().id
    person_schema = PersonSchema()
    group_schema = GroupSchema()
    member_schema = MemberSchema()
    manager_schema = ManagerSchema()

    max_person_id = max([pair[1] for pair in group_members + group_managers])
    max_group_id = max([pair[0] for pair in group_members + group_managers])
    # create people
    people = []
    for i in range(1, max_person_id + 1):
        person_name = f"Person{i}"
        person = Person(
            **person_schema.load(person_object_factory(person_name)))
        person.username = person_name  # for testing purpose
        person.password = person_name  # for testing purpose
        sqla.add(person)
        people.append(person)

    # create groups
    groups = []
    for i in range(1, max_group_id + 1):
        group_name = f"Group{i}"
        group = Group(**group_schema.load(
            group_object_factory(group_type_id, name=group_name, active=True)))
        sqla.add(group)
        groups.append(group)
    sqla.commit()

    # create members: (groupIdx, personIdx)
    for group_id, person_id in group_members:
        member = Member(**member_schema.load(member_object_factory(
            person_id,
            group_id)))
        sqla.add(member)
        print(member)

    # create managers: (groupIdx, personIdx)
    for group_id, person_id in group_managers:
        manager = Manager(**manager_schema.load(manager_object_factory(
            person_id,
            group_id,
            manager_type_id)))
        sqla.add(manager)
        print(manager)

    sqla.commit()

# Create test data that is used in front-end testing


def create_hierarchy_test_case_1(sqla):
    group_members = [
        [1, 1],
        [1, 3],
        [1, 4],
        [2, 2],
        [2, 5],
        [3, 6],
        [3, 2],
        [4, 2],
        [9, 9]
    ]
    group_managers = [
        [1, 1],
        [2, 1],
        [3, 1],
        [4, 6],
        [9, 8]
    ]
    create_hierarchical_groups_and_participants(
        sqla,
        group_members,
        group_managers)


def create_hierarchy_test_case_2(sqla):
    group_members = [
        [1, 1],
        [2, 3],
    ]
    group_managers = [
        [2, 1],
        [1, 2],
        [1, 3],
    ]
    create_hierarchical_groups_and_participants(
        sqla,
        group_members,
        group_managers
    )


def create_group_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_group_types(sqla, 5)
    create_multiple_manager_types(sqla, 5)

    # # create leadership hierarchy data
    # create_hierarchy_test_case_1(sqla)

    # # create faker data
    # create_multiple_groups(sqla, 10)
    # create_multiple_managers(sqla, 0.75)
    # create_multiple_members(sqla, 0.75)

    # create member histories
    create_multiple_member_histories(sqla, 30)

    create_multiple_meetings(sqla, 12)
    create_multiple_attendance(sqla, 0.75)

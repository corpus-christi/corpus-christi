from .. import db
from .models import Member, Manager


def is_overseer(person_id, group_id):
    return group_id in get_all_subgroups(person_id)


def get_all_subgroups(person_id):
    """get all groups where the person is an overseer of

    :person_id: the person's id
    :managers: an iterable of managers
    :members: an iterable of members
    :returns: a set of integers which is the ids of the subgroups

    """
    all_members = db.session.query(Member).filter_by(active=True).all()
    all_managers = db.session.query(Manager).filter_by(active=True).all()

    # a map from group_id => members, where members is a set of person_ids
    group_member_map = {}
    # a map from person_id => leading_groups, where leading_groups is a set of
    # group_ids
    leading_group_map = {}

    for member in all_members:
        if member.group_id not in group_member_map:
            group_member_map[member.group_id] = set()
        group_member_map[member.group_id].add(member.person_id)

    for manager in all_managers:
        if manager.person_id not in leading_group_map:
            leading_group_map[manager.person_id] = set()
        leading_group_map[manager.person_id].add(manager.group_id)

    searched_groups = set()
    searched_persons = set()

    def search_person(person_id):
        if person_id in searched_persons:
            return
        searched_persons.add(person_id)
        for group_id in leading_group_map.get(person_id, []):
            search_group(group_id)

    def search_group(group_id):
        if group_id in searched_groups:
            return
        searched_groups.add(group_id)
        for person_id in group_member_map.get(group_id, []):
            search_person(person_id)

    search_person(person_id)
    return searched_groups

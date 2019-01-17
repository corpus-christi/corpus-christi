import datetime

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import groups
from .models import GroupSchema, Group, Attendance, Member, MemberSchema, Meeting, MeetingSchema, AttendanceSchema
from ..people.models import Role
from .. import db

# ---- Group

group_schema = GroupSchema()

def group_dump(group):
    group.managerInfo = group.manager
    group.managerInfo.person = group.manager.account.person
    group.memberList = group.members
    return jsonify(group_schema.dump(group))



@groups.route('/groups', methods=['POST'])
@jwt_required
def create_group():
    request.json['active'] = True

    members_to_add = None
    if 'member_ids' in request.json.keys():
        members_to_add = request.json['member_ids']
        del request.json['member_ids']

    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_group = Group(**valid_group)
    
    db.session.add(new_group)
    db.session.commit()

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    if members_to_add is not None:
        for member in members_to_add:
            new_member = generate_member(new_group.id, member, today, True)
            db.session.add(new_member)

    group_overseer = db.session.query(Role).filter_by(name_i18n="role.group-overseer").first()
    manager_roles = new_group.manager.account.roles

    if group_overseer:
        if group_overseer not in manager_roles:
            print("adding role", end='\n\n\n')
            manager_roles.append(group_overseer)

    db.session.add(new_group.manager.account)
    db.session.commit()
    return group_dump(new_group), 201


@groups.route('/groups')
@jwt_required
def read_all_groups():
    result = db.session.query(Group).all()
    for group in result:
        group.memberList = group.members
        group.managerInfo = group.manager
        group.managerInfo.person = group.manager.account.person
    return jsonify(group_schema.dump(result, many=True))


@groups.route('/groups/<group_id>')
@jwt_required
def read_one_group(group_id):
    result = db.session.query(Group).filter_by(id=group_id).first()
    return group_dump(result), 200


@groups.route('/groups/<group_id>', methods=['PATCH'])
@jwt_required
def update_group(group_id):
    
    update_members = None
    if 'member_ids' in request.json.keys():
        update_members = request.json['member_ids']
        del request.json['member_ids']
    
    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    group = db.session.query(Group).filter_by(id=group_id).first()

    old_members = []
    for member in group.members:
        old_members.append({member.person_id : member.joined})

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    print(old_members, end='\n\n\n')
    if update_members is not None:
        for member in group.members:
            db.session.delete(member)
        for member in update_members:
            if member in old_members:
                date = old_members[member]
            else:
                date = today
            
            new_member = generate_member(group.id, member, date, True)
            db.session.add(new_member)

    for key, val in valid_group.items():
        setattr(group, key, val)

    db.session.commit()
    return group_dump(group), 201


@groups.route('/groups/activate/<group_id>', methods=['PUT'])
@jwt_required
def activate_group(group_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    
    if group is None:
        return jsonify(msg="Group not found"), 404
    setattr(group, 'active', True)
    return jsonify(group_schema.dump(group))


@groups.route('/groups/deactivate/<group_id>', methods=['PUT'])
@jwt_required
def deactivate_group(group_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    
    if group is None:
        return jsonify(msg="Group not found"), 404
    setattr(group, 'active', False)
    return jsonify(group_schema.dump(group))


# ---- Meeting

meeting_schema = MeetingSchema()


@groups.route('/meetings', methods=['POST'])
@jwt_required
def create_meeting():
    try:
        valid_meeting = meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_meeting = Meeting(**valid_meeting)
    db.session.add(new_meeting)
    db.session.commit()
    return jsonify(meeting_schema.dump(new_meeting)), 201


@groups.route('/meetings')
@jwt_required
def read_all_meetings():
    result = db.session.query(Meeting).all()
    return jsonify(meeting_schema.dump(result, many=True))

@groups.route('/meetings/group/<group_id>')
@jwt_required
def read_all_meetings_by_group(group_id):
    result = db.session.query(Meeting).filter_by(group_id=group_id).all()
    return jsonify(meeting_schema.dump(result, many=True))


@groups.route('/meetings/address/<address_id>')
@jwt_required
def read_all_meetings_by_location(address_id):
    result = db.session.query(Meeting).filter_by(address_id=address_id).all()
    return jsonify(meeting_schema.dump(result, many=True))


@groups.route('/meetings/<meeting_id>')
@jwt_required
def read_one_meeting(meeting_id):
    result = db.session.query(Meeting).filter_by(id=meeting_id).first()
    return jsonify(meeting_schema.dump(result))


@groups.route('/meetings/<meeting_id>', methods=['PATCH'])
@jwt_required
def update_meeting(meeting_id):
    try:
        valid_meeting = meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()

    for key, val in valid_meeting.items():
        setattr(meeting, key, val)

    db.session.commit()
    return jsonify(meeting_schema.dump(meeting))


# ---- Member

member_schema = MemberSchema()


def generate_member(group_id, person_id, joined, active):
    member = {}
    member['group_id'] = group_id
    member['person_id'] = person_id
    member['joined'] = joined
    member['active'] = active
    member = Member(**member_schema.load(member))
    return member


@groups.route('/members', methods=['POST'])
@jwt_required
def create_member():
    request.json['active'] = True
    try:
        valid_member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_member = Member(**valid_member)
    db.session.add(new_member)
    db.session.commit()
    return jsonify(member_schema.dump(new_member)), 201


@groups.route('/members')
@jwt_required
def read_all_members():
    result = db.session.query(Member).all()
    return jsonify(member_schema.dump(result, many=True))


@groups.route('/members/<member_id>')
@jwt_required
def read_one_member(member_id):
    result = db.session.query(Member).filter_by(id=member_id).first()
    return jsonify(member_schema.dump(result))


@groups.route('/members/<member_id>', methods=['PATCH'])
@jwt_required
def update_member(member_id):
    try:
        valid_member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    member = db.session.query(Member).filter_by(id=member_id).first()

    for key, val in valid_member.items():
        setattr(member, key, val)

    db.session.commit()
    return jsonify(member_schema.dump(member))


# ---- Attendance

attendance_schema = AttendanceSchema()


@groups.route('/attendance', methods=['POST'])
@jwt_required
def create_attendance():
    try:
        valid_attendance = attendance_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_attendance = Attendance(**valid_attendance)
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify(attendance_schema.dump(new_attendance)), 201


@groups.route('/attendance')
@jwt_required
def read_all_attendance():
    result = db.session.query(Attendance).all()
    return jsonify(attendance_schema.dump(result, many=True))


@groups.route('/attendance/meeting/<meeting_id>')
@jwt_required
def read_attendance_by_meeting(meeting_id):
    result = db.session.query(Attendance).filter_by(meeting_id=meeting_id).all()
    return jsonify(attendance_schema.dump(result, many=True))

@groups.route('/attendance/member/<member_id>')
@jwt_required
def read_attendance_by_member(member_id):
    result = db.session.query(Attendance).filter_by(member_id=member_id).all()
    return jsonify(attendance_schema.dump(result, many=True))

@groups.route('/attendance/<attendance_id>', methods=['PATCH'])
@jwt_required
def update_attendance(attendance_id):
    try:
        valid_attendance = attendance_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    attendance = db.session.query(Attendance).filter_by(id=attendance_id).first()

    for key, val in valid_attendance.items():
        setattr(attendance, key, val)

    db.session.commit()
    return jsonify(attendance_schema.dump(attendance))

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import groups
from .models import GroupSchema, Group, Attendance, Member, MemberSchema, Meeting, MeetingSchema, AttendanceSchema
from .. import db

# ---- Group

group_schema = GroupSchema()


@groups.route('/groups', methods=['POST'])
@jwt_required
def create_group():
    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_group = Group(**valid_group)
    db.session.add(new_group)
    db.session.commit()
    return jsonify(group_schema.dump(new_group)), 201


@groups.route('/groups')
@jwt_required
def read_all_groups():
    result = db.session.query(Group).all()
    return jsonify(group_schema.dump(result, many=True))


@groups.route('/groups/<group_id>')
@jwt_required
def read_one_group(group_id):
    result = db.session.query(Group).filter_by(id=group_id).first()
    return jsonify(group_schema.dump(result))


@groups.route('/groups/<group_id>', methods=['PATCH'])
@jwt_required
def update_group(group_id):
    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    group = db.session.query(Group).filter_by(id=group_id).first()

    for key, val in valid_group.items():
        setattr(group, key, val)

    db.session.commit()
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


@groups.route('/members', methods=['POST'])
@jwt_required
def create_member():
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


@groups.route('/attendance/<attendance_id>')
@jwt_required
def read_one_attendance(attendance_id):
    result = db.session.query(Attendance).filter_by(id=attendance_id).first()
    return jsonify(attendance_schema.dump(result))


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

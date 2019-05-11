import datetime

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import groups
from .models import GroupSchema, Group, Attendance, Member, MemberSchema, Meeting, MeetingSchema, AttendanceSchema
from ..people.models import Role, Manager, Account
from ..images.models import Image, ImageSchema, ImageGroup, ImageGroupSchema
from .. import db

# ---- Group

group_schema = GroupSchema()

def group_dump(group):
    group.managerInfo = group.manager
    group.managerInfo.person = group.manager.person
    group.memberList = group.members
    return jsonify(group_schema.dump(group))



@groups.route('/groups', methods=['POST'])
@jwt_required
def create_group():
    request.json['active'] = True
    members_to_add = None
    if 'person_ids' in request.json.keys():
        members_to_add = request.json['person_ids']
        del request.json['person_ids']

    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_group = Group(**valid_group)

    if db.session.query(Manager).filter_by(id=new_group.manager_id).first() is None:
        return jsonify(msg="Manager not found"), 404
    
    db.session.add(new_group)

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    if members_to_add is not None:
        for member in members_to_add:
            new_member = generate_member(new_group.id, member, today, True)
            db.session.add(new_member)

    # Add group_overseer role to the existing manager account -> if they have an account
    group_overseer = db.session.query(Role).filter_by(name_i18n="role.group-overseer").first()
    subq = db.session.query(Manager.person_id).filter_by(id=new_group.manager_id).subquery()
    manager_account = db.session.query(Account).filter(Account.person_id.in_(subq)).first()
    
    if manager_account:
        manager_roles = manager_account.roles
        if group_overseer and group_overseer not in manager_roles:
                manager_roles.append(group_overseer)
                setattr(manager_account, 'roles', manager_roles)
                print("adding group overseer role", end='\n\n\n')

    # db.session.add(manager_account)
    db.session.commit()
    return group_dump(new_group), 201


@groups.route('/groups')
def read_all_groups():
    query = db.session.query(Group)
    return_group = request.args.get('return_group')
    if return_group == 'inactive':
        query = query.filter_by(active=False)
    elif return_group in ('all', 'both'):
        pass # Don't filter
    else:
        query = query.filter_by(active=True)
    query = query.all()
    
    for group in query:
        group.memberList = group.members
        group.managerInfo = group.manager
        group.managerInfo.person = group.manager.person
    return jsonify(group_schema.dump(query, many=True))


@groups.route('/groups/<group_id>')
@jwt_required
def read_one_group(group_id):
    result = db.session.query(Group).filter_by(id=group_id).first()
    if result is None:
        return jsonify(msg="Group not found"), 404
    return group_dump(result), 200


@groups.route('/groups/<group_id>', methods=['PATCH'])
@jwt_required
def update_group(group_id):
    
    # fetch the optional 'person_ids' field in the request object
    update_person_ids = [] 
    if 'person_ids' in request.json.keys():
        update_person_ids = request.json['person_ids']
        del request.json['person_ids']
    
    try:
        valid_group = group_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    group = db.session.query(Group).filter_by(id=group_id).first()
    if group is None:
        return jsonify(msg="Group not found"), 404

    new_manager_id = None
    # fetch 'manager_id' from the request object
    if 'manager_id' in request.json.keys():
        new_manager_id = request.json['manager_id']
    if db.session.query(Manager).filter_by(id=new_manager_id).first() is None:
        return jsonify(msg="Manager not found"), 404

    # if the manager changed, then try to add the overseer role to the manager's account
    if new_manager_id and new_manager_id is not group.manager_id:
        group_overseer = db.session.query(Role).filter_by(name_i18n="role.group-overseer").first()
        if group_overseer:
            manager = db.session.query(Manager).filter_by(id=new_manager_id).first()
            manager_account = db.session.query(Account).filter_by(person_id=manager.person_id).first()
            if manager_account:
                manager_roles = manager_account.roles
                if group_overseer not in manager_roles:
                    manager_roles.append(group_overseer)
                    setattr(manager_account, 'roles', manager_roles)
                    print("adding group overseer role", end='\n\n\n')

    old_member_joined_dates = []
    for member in group.members:
        old_member_joined_dates.append({member.person_id : member.joined})

    old_person_ids = [ member.person_id for member in group.members ]
    print(f"old person ids: {old_person_ids}")
    print(f"new person ids: {update_person_ids}")


    today = datetime.datetime.today().strftime('%Y-%m-%d')

    # for each update_person_id, if it already exists, skip, otherwise, add
    # this way it keeps the original member_id unchanged
    if update_person_ids != []:
        for update_person_id in update_person_ids:
            if update_person_id not in old_person_ids:
                new_member = generate_member(group.id, update_person_id, today, True)
                db.session.add(new_member)
            else:
                print(f"NEW ID: {update_person_id}")
                new_member = db.session.query(Member).filter_by(person_id=update_person_id, group_id=group_id).first()
                setattr(new_member,'active', True)

    if update_person_ids != []:
        for old_person_id in old_person_ids:
            if old_person_id not in update_person_ids:
                delete_member = db.session.query(Member).filter_by(group_id=group.id, person_id=old_person_id).first()
                setattr(delete_member, 'active', False)

    # set other attributes
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
    db.session.commit()
    return jsonify(group_schema.dump(group))


@groups.route('/groups/deactivate/<group_id>', methods=['PUT'])
@jwt_required
def deactivate_group(group_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    
    if group is None:
        return jsonify(msg="Group not found"), 404

    setattr(group, 'active', False)
    db.session.commit()
    return jsonify(group_schema.dump(group))


# ---- Meeting

meeting_schema = MeetingSchema()


@groups.route('/meetings', methods=['POST'])
@jwt_required
def create_meeting():
    if 'active' not in request.json.keys():
        request.json['active']=True
    try:
        valid_meeting = meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_meeting = Meeting(**valid_meeting)
    db.session.add(new_meeting)
    db.session.commit()
    return jsonify(meeting_schema.dump(new_meeting)), 201


@groups.route('/meetings')
def read_all_meetings():
    result = db.session.query(Meeting).all()

    if result == []:
        return jsonify(msg="No meetings found"), 404

    for r in result:
        r.address = r.address
    return jsonify(meeting_schema.dump(result, many=True))

@groups.route('/meetings/group/<group_id>')
@jwt_required
def read_all_meetings_by_group(group_id):
    result = db.session.query(Meeting).filter_by(group_id=group_id).all()

    if len(result) == 0:
            return jsonify(msg="No meetings found"), 404

    for r in result:
        r.address = r.address

    return jsonify(meeting_schema.dump(result, many=True))


@groups.route('/meetings/address/<address_id>')
@jwt_required
def read_all_meetings_by_location(address_id):
    result = db.session.query(Meeting).filter_by(address_id=address_id).all()

    if len(result) == 0:
        return jsonify(msg="No meetings found"), 404

    return jsonify(meeting_schema.dump(result, many=True))


@groups.route('/meetings/<meeting_id>')
@jwt_required
def read_one_meeting(meeting_id):
    result = db.session.query(Meeting).filter_by(id=meeting_id).first()

    if result is None:
        return jsonify(msg="Meeting not found"), 404

    result.address = result.address

    return jsonify(meeting_schema.dump(result))


@groups.route('/meetings/<meeting_id>', methods=['PATCH'])
@jwt_required
def update_meeting(meeting_id):
    try:
        valid_meeting = meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()

    if meeting is None:
        return jsonify(msg="Meeting not found"), 404

    for key, val in valid_meeting.items():
        setattr(meeting, key, val)

    db.session.commit()
    return jsonify(meeting_schema.dump(meeting))


@groups.route('/meetings/delete/<meeting_id>', methods=['DELETE'])
@jwt_required
def delete_meeting(meeting_id):
    # USE WITH CARE!!! --- WILL DELETE MEETING AND ALL ATTENDANCE TO THAT MEETING
    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()
    
    if meeting is None:
        return jsonify(msg='Meeting not found'), 404
    
    for member in meeting.members:
        db.session.delete(member)
    db.session.delete(meeting)
    db.session.commit()
    
    return jsonify(msg='Meeting ' + meeting_id + ' deleted'), 200


@groups.route('/meetings/activate/<meeting_id>', methods=['PUT'])
@jwt_required
def activate_meeting(meeting_id):
    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()
    
    if meeting is None:
        return jsonify(msg="Meeting not found"), 404

    setattr(meeting, 'active', True)
    db.session.commit()
    return jsonify(meeting_schema.dump(meeting))


@groups.route('/meetings/deactivate/<meeting_id>', methods=['PUT'])
@jwt_required
def deactivate_meeting(meeting_id):
    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()
    
    if meeting is None:
        return jsonify(msg="Meeting not found"), 404

    setattr(meeting, 'active', False)
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

    if db.session.query(Member).filter_by(\
            group_id=valid_member["group_id"],
            person_id= valid_member["person_id"]
            ).count() != 0:
        return 'member already exists', 409

    new_member = Member(**valid_member)
    db.session.add(new_member)
    db.session.commit()
    return jsonify(member_schema.dump(new_member)), 201


@groups.route('/members')
@jwt_required
def read_all_members():
    result = db.session.query(Member).all()

    if result == []:
        return jsonify(msg="No members found"), 404

    return jsonify(member_schema.dump(result, many=True))


@groups.route('/members/<member_id>')
@jwt_required
def read_one_member(member_id):
    result = db.session.query(Member).filter_by(id=member_id).first()

    if result is None:
        return jsonify(msg="No members found"), 404

    return jsonify(member_schema.dump(result))


@groups.route('/members/<member_id>', methods=['PATCH'])
@jwt_required
def update_member(member_id):
    try:
        valid_member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    member = db.session.query(Member).filter_by(id=member_id).first()

    if member is None:
        return jsonify(msg="No members found"), 404

    for key, val in valid_member.items():
        setattr(member, key, val)

    db.session.commit()
    return jsonify(member_schema.dump(member))


@groups.route('/members/activate/<member_id>', methods=['PUT'])
@jwt_required
def activate_member(member_id):
    member = db.session.query(Member).filter_by(id=member_id).first()
    
    if member is None:
        return jsonify(msg="Member not found"), 404

    setattr(member, 'active', True)
    db.session.commit()
    return jsonify(member_schema.dump(member))


@groups.route('/members/deactivate/<member_id>', methods=['PUT'])
@jwt_required
def deactivate_member(member_id):
    member = db.session.query(Member).filter_by(id=member_id).first()
    
    if member is None:
        return jsonify(msg="Member not found"), 404

    setattr(member, 'active', False)
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

    if db.session.query(Attendance).filter_by(\
            meeting_id=valid_attendance["meeting_id"],
            member_id=valid_attendance["member_id"]
            ).count() != 0:
        return 'attendance already exists', 409

    new_attendance = Attendance(**valid_attendance)
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify(attendance_schema.dump(new_attendance)), 201


@groups.route('/attendance')
@jwt_required
def read_all_attendance():
    result = db.session.query(Attendance).all()

    if result == []:
        return jsonify(msg="No attendance records found"), 404

    return jsonify(attendance_schema.dump(result, many=True))


@groups.route('/attendance/meeting/<meeting_id>')
@jwt_required
def read_attendance_by_meeting(meeting_id):
    result = db.session.query(Attendance).filter_by(meeting_id=meeting_id).all()

    if result == []:
        return jsonify(msg="No attendance records found"), 404

    return jsonify(attendance_schema.dump(result, many=True))

@groups.route('/attendance/member/<member_id>')
@jwt_required
def read_attendance_by_member(member_id):
    result = db.session.query(Attendance).filter_by(member_id=member_id).all()

    if result == []:
        return jsonify(msg="No attendance records found"), 404

    return jsonify(attendance_schema.dump(result, many=True))

@groups.route('/attendance', methods=['DELETE'])
@jwt_required
def delete_attendance():
    try:
        valid_attendance = attendance_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    meeting_id = valid_attendance["meeting_id"]
    member_id = valid_attendance["member_id"]

    result = db.session.query(Attendance).filter_by(meeting_id=meeting_id, \
            member_id=member_id
            ).first()

    if not result:
        return f"Attendance with member_id {member_id} and meeting_id {meeting_id} doesn't exist", 404

    db.session.delete(result)
    db.session.commit()

    # 204 codes don't respond with any content
    return jsonify(attendance_schema.dump(valid_attendance)), 204

# ---- Image

@groups.route('/<group_id>/images/<image_id>', methods=['POST'])
@jwt_required
def add_group_images(group_id, image_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    image = db.session.query(Image).filter_by(id=image_id).first()

    group_image = db.session.query(ImageGroup).filter_by(group_id=group_id,image_id=image_id).first()

    if not group:
        return jsonify(f"Group with id #{group_id} does not exist."), 404

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    # If image is already attached to the group
    if group_image:
        return jsonify(f"Image with id#{image_id} is already attached to group with id#{group_id}."), 422
    else:
        new_entry = ImageGroup(**{'group_id': group_id, 'image_id': image_id})
        db.session.add(new_entry)
        db.session.commit()

    return jsonify(f"Image with id #{image_id} successfully added to Group with id #{group_id}."), 201

@groups.route('/<group_id>/images/<image_id>', methods=['PUT'])
@jwt_required
def put_group_images(group_id, image_id):
    # check for old image id in parameter list (?old=<id>)
    old_image_id = request.args['old']
    new_image_id = image_id

    if old_image_id == 'false':
        post_resp = add_group_images(group_id, new_image_id)
        return jsonify({'deleted': 'No image to delete', 'posted': str(post_resp[0].data, "utf-8") })
    else:
        del_resp = delete_group_image(group_id, old_image_id)
        post_resp = add_group_images(group_id, new_image_id)

        return jsonify({'deleted': del_resp[0], 'posted': str(post_resp[0].data, "utf-8") })

@groups.route('/<group_id>/images/<image_id>', methods=['DELETE'])
@jwt_required
def delete_group_image(group_id, image_id):
    group_image = db.session.query(ImageGroup).filter_by(group_id=group_id,image_id=image_id).first()
    
    if not group_image:
        return jsonify(f"Image with id #{image_id} is not assigned to Group with id #{group_id}."), 404

    db.session.delete(group_image)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed image', 204

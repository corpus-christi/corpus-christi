import datetime

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import groups
from .models import Group, GroupSchema, Attendance, Member, MemberSchema, Meeting, MeetingSchema, AttendanceSchema, Manager, ManagerSchema, GroupType, GroupTypeSchema, ManagerType, ManagerTypeSchema
from .. import db
from ..images.models import Image, ImageGroup
from ..people.models import Role, Person
from src.shared.helpers import modify_entity, get_all_queried_entities, logged_response

from src.shared.models import QueryArgumentError

from sqlalchemy.exc import IntegrityError, DBAPIError

# ---- Group Type

group_type_schema = GroupTypeSchema()

@groups.route('/group-types', methods=['POST'])
def create_group_type():
    try:
        valid_group_type = group_type_schema.load(request.json)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    new_group_type = GroupType(**valid_group_type)
    db.session.add(new_group_type)
    db.session.commit()
    return logged_response(group_type_schema.dump(new_group_type), 201)

@groups.route('/group-types/<int:group_type_id>', methods=['GET'])
def read_one_group_type(group_type_id):
    group_type = db.session.query(GroupType).filter_by(id=group_type_id).first()
    if not group_type:
        return logged_response(f"GroupType with id #{group_type_id} does not exist.", 404)

    return logged_response(group_type_schema.dump(group_type))

@groups.route('/group-types', methods=['GET'])
def read_all_group_types():
    query = db.session.query(GroupType)
    try:
        group_types = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    return logged_response(group_type_schema.dump(group_types, many=True))

@groups.route('/group-types/<int:group_type_id>', methods=['PATCH'])
@jwt_required
def update_group_type(group_type_id):
    group_type_schema = GroupTypeSchema()

    try:
        valid_attributes = group_type_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    group_type = db.session.query(GroupType).filter_by(id=group_type_id).first()

    if not group_type:
        return logged_response(f"GroupType with id #{group_type_id} does not exist.", 404)

    for key, val in valid_attributes.items():
        setattr(group_type, key, val)

    db.session.add(group_type)
    db.session.commit()

    return logged_response(group_type_schema.dump(group_type), 200)


@groups.route('/group-types/<int:group_type_id>', methods=['DELETE'])
@jwt_required
def delete_group_type(group_type_id):
    group_type = db.session.query(GroupType).filter_by(id=group_type_id).first()

    if not group_type:
        return logged_response(f"GroupType with id #{group_type_id} does not exist.", 404)

    db.session.delete(group_type)
    db.session.commit()

    # 204 codes don't respond with any content
    return logged_response("Deleted successfully", 204)

# ---- Group

group_schema = GroupSchema()

@groups.route('/groups', methods=['POST'])
@jwt_required
def create_group():
    try:
        valid_group = group_schema.load(request.json, partial=['active'])
    except ValidationError as err:
        return logged_response(err.messages, 422)

    if 'active' not in valid_group:
        valid_group['active'] = True

    new_group = Group(**valid_group)

    db.session.add(new_group)

    try:
        db.session.commit()
    # when the foreign key given is invalid
    except IntegrityError:
        return logged_response('Payload contains an invalid group type', 404)

    return logged_response(group_schema.dump(new_group), 201)


@groups.route('/groups', methods=['GET'])
def read_all_groups():
    query = db.session.query(Group)
    try:
        groups = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    group_schema = GroupSchema()
    return logged_response(group_schema.dump(groups, many=True), 200)


@groups.route('/groups/<int:group_id>', methods=['GET'])
@jwt_required
def read_one_group(group_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    if group is None:
        return logged_response(f"Group with id {group_id} does not exist", 404)
    return logged_response(group_schema.dump(group), 200)

@groups.route('/groups/<int:group_id>', methods=['PATCH'])
@jwt_required
def update_group(group_id):
    group_schema = GroupSchema()

    try:
        valid_attributes = group_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    group = db.session.query(Group).filter_by(id=group_id).first()

    if not group:
        return logged_response(f"Group with id #{group_id} does not exist.", 404)

    for key, val in valid_attributes.items():
        setattr(group, key, val)

    db.session.add(group)
    db.session.commit()

    return logged_response(group_schema.dump(group), 200)

@groups.route('/groups/<int:group_id>', methods=['DELETE'])
@jwt_required
def delete_group(group_id):
    group = db.session.query(Group).filter_by(id=group_id).first()

    if group is None:
        return logged_response(f"Group with id #{group_id} does not exist", 404)

    db.session.delete(group)
    db.session.commit()

    # no content should be in the response with 204 status code
    return logged_response("Deleted successfully", 204)

# ---- Manager Type

manager_type_schema = ManagerTypeSchema()

@groups.route('/manager-types', methods=['POST'])
def create_manager_type():
    try:
        valid_manager_type = manager_type_schema.load(request.json)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    new_manager_type = ManagerType(**valid_manager_type)
    db.session.add(new_manager_type)
    db.session.commit()
    return logged_response(manager_type_schema.dump(new_manager_type), 201)

@groups.route('/manager-types/<int:manager_type_id>', methods=['GET'])
def read_one_manager_type(manager_type_id):
    manager_type = db.session.query(ManagerType).filter_by(id=manager_type_id).first()
    if not manager_type:
        return logged_response(f"ManagerType with id #{manager_type_id} does not exist.", 404)

    return logged_response(manager_type_schema.dump(manager_type))

@groups.route('/manager-types', methods=['GET'])
def read_all_manager_types():
    query = db.session.query(ManagerType)
    try:
        manager_types = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    return logged_response(manager_type_schema.dump(manager_types, many=True))

@groups.route('/manager-types/<int:manager_type_id>', methods=['PATCH'])
@jwt_required
def update_manager_type(manager_type_id):
    manager_type_schema = ManagerTypeSchema()

    try:
        valid_attributes = manager_type_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    manager_type = db.session.query(ManagerType).filter_by(id=manager_type_id).first()

    if not manager_type:
        return logged_response(f"ManagerType with id #{manager_type_id} does not exist.", 404)

    for key, val in valid_attributes.items():
        setattr(manager_type, key, val)

    db.session.add(manager_type)
    db.session.commit()

    return logged_response(manager_type_schema.dump(manager_type), 200)


@groups.route('/manager-types/<int:manager_type_id>', methods=['DELETE'])
@jwt_required
def delete_manager_type(manager_type_id):
    manager_type = db.session.query(ManagerType).filter_by(id=manager_type_id).first()

    if not manager_type:
        return logged_response(f"ManagerType with id #{manager_type_id} does not exist.", 404)

    db.session.delete(manager_type)
    db.session.commit()

    # 204 codes don't respond with any content
    return logged_response("Deleted successfully", 204)


# ---- Manager

manager_schema = ManagerSchema()


@groups.route('/groups/<int:group_id>/managers', methods=['POST'])
@jwt_required
def create_manager(group_id):
    # make group_id an invalid field in payload
    manager_schema = ManagerSchema(exclude=['group_id'])
    try:
        valid_manager = manager_schema.load(request.json, partial=['active'])
    except ValidationError as err:
        return logged_response(err.messages, 422)

    person_id = valid_manager['person_id']

    if db.session.query(Manager).filter_by(person_id=person_id, group_id=group_id).first():
        # if the same manager already exists
        return logged_response(f"Manager with group_id #{group_id} and person_id #{person_id} already exists", 409)

    if 'active' not in valid_manager:
        valid_manager['active'] = True

    new_manager = Manager(group_id=group_id, **valid_manager)
    db.session.add(new_manager)
    try:
        db.session.commit()
    except IntegrityError:
        return logged_response('Payload contains an invalid group/person key', 404)
    return logged_response(manager_schema.dump(new_manager), 201)


@groups.route('/groups/<int:group_id>/managers', methods=['GET'])
@jwt_required
def read_all_managers(group_id):
    query = db.session.query(Manager).filter_by(group_id=group_id)
    try:
        managers = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    return logged_response(manager_schema.dump(managers, many=True))


@groups.route('/groups/<int:group_id>/managers/<int:person_id>', methods=['GET'])
@jwt_required
def read_one_manager(group_id, person_id):
    manager = db.session.query(Manager).filter_by(group_id=group_id, person_id=person_id).first()
    if manager is None:
        return logged_response(f"Manager with group_id #{group_id} and person_id #{person_id} does not exist", 404)
    return logged_response(manager_schema.dump(manager))


@groups.route('/groups/<int:group_id>/managers/<int:person_id>', methods=['PATCH'])
@jwt_required
def update_manager(group_id, person_id):
    manager_schema = ManagerSchema()
    try:
        valid_attributes = manager_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    manager = db.session.query(Manager).filter_by(group_id=group_id, person_id=person_id).first()
    if manager is None:
        return logged_response(f"Manager with group_id #{group_id} and person_id #{person_id} does not exist", 404)

    new_group_id = valid_attributes.get('group_id')
    new_person_id = valid_attributes.get('person_id')
    # if modifying manager identity or belonging group
    if new_group_id or new_person_id:
        # check if entry already exists
        if db.session.query(Manager).filter_by(
                person_id=new_person_id or person_id, 
                group_id=new_group_id or group_id).first():
            return logged_response(f"Manager with group_id #{new_group_id} and person_id #{new_person_id} already exists", 409)
        # check if the new group exists
        if new_group_id and not db.session.query(Group).filter_by(id=new_group_id).first():
            return logged_response(f"Group with group_id #{new_group_id} does not exist", 404)
        # check if the new person exists
        if new_person_id and not db.session.query(Person).filter_by(id=new_person_id).first():
            return logged_response(f"Person with person_id #{new_person_id} does not exist", 404)


    for key, val in valid_attributes.items():
        setattr(manager, key, val)

    db.session.add(manager)
    db.session.commit()

    return logged_response(manager_schema.dump(manager), 200)


@groups.route('/groups/<int:group_id>/managers/<int:person_id>', methods=['DELETE'])
@jwt_required
def delete_manager(group_id, person_id):
    manager = db.session.query(Manager).filter_by(group_id=group_id, person_id=person_id).first()

    if manager is None:
        return logged_response(f"Manager with group_id #{group_id} and person_id #{person_id} does not exist", 404)

    db.session.delete(manager)
    db.session.commit()

    # no content should be in the response with 204 status code
    return logged_response("Deleted successfully", 204)

# ---- Meeting

meeting_schema = MeetingSchema()


@groups.route('/meetings', methods=['POST'])
@jwt_required
def create_meeting():
    try:
        valid_meeting = meeting_schema.load(request.json, partial=['active'])
    except ValidationError as err:
        return logged_response(err.messages, 422)

    if 'active' not in valid_meeting:
        valid_meeting['active'] = True

    new_meeting = Meeting(**valid_meeting)

    db.session.add(new_meeting)

    try:
        db.session.commit()
    # when the foreign key given is invalid
    except IntegrityError:
        return logged_response('Payload contains an invalid address/group key', 404)

    return logged_response(meeting_schema.dump(new_meeting), 201)

@groups.route('/meetings', methods=['GET'])
def read_all_meetings():
    query = db.session.query(Meeting)
    try:
        meetings = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    meeting_schema = MeetingSchema()
    return logged_response(meeting_schema.dump(meetings, many=True), 200)

@groups.route('/meetings/<int:meeting_id>', methods=['GET'])
@jwt_required
def read_one_meeting(meeting_id):
    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()
    if meeting is None:
        return logged_response(f"Meeting with id {meeting_id} does not exist", 404)
    return logged_response(meeting_schema.dump(meeting), 200)

@groups.route('/meetings/<int:meeting_id>', methods=['PATCH'])
@jwt_required
def update_meeting(meeting_id):
    meeting_schema = MeetingSchema()

    try:
        valid_attributes = meeting_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()

    if not meeting:
        return logged_response(f"Meeting with id #{meeting_id} does not exist.", 404)

    for key, val in valid_attributes.items():
        setattr(meeting, key, val)

    db.session.add(meeting)
    db.session.commit()

    return logged_response(meeting_schema.dump(meeting), 200)

@groups.route('/meetings/<int:meeting_id>', methods=['DELETE'])
@jwt_required
def delete_meeting(meeting_id):
    meeting = db.session.query(Meeting).filter_by(id=meeting_id).first()

    if meeting is None:
        return logged_response(f"Meeting with id #{meeting_id} does not exist", 404)

    db.session.delete(meeting)
    db.session.commit()

    # no content should be in the response with 204 status code
    return logged_response("Deleted successfully", 204)

# ---- Member

member_schema = MemberSchema()


@groups.route('/groups/<int:group_id>/members', methods=['POST'])
@jwt_required
def create_member(group_id):
    member_schema = MemberSchema(exclude=['group_id'])
    try:
        valid_member = member_schema.load(request.json, partial=['joined', 'active']) # make joined and active optional fields
    except ValidationError as err:
        return logged_response(err.messages, 422)
    person_id = valid_member['person_id']
    if db.session.query(Member).filter_by(person_id=person_id, group_id=group_id).first():
        # if the same member already exists
        return logged_response(f"Member with group_id #{group_id} and person_id #{person_id} already exists", 409)

    if 'joined' not in valid_member:
        valid_member['joined'] = datetime.date.today()

    if 'active' not in valid_member:
        valid_member['active'] = True

    new_member = Member(group_id=group_id, **valid_member)
    db.session.add(new_member)
    try:
        db.session.commit()
    except IntegrityError:
        return logged_response('Payload contains an invalid group/person key', 404)
    return logged_response(member_schema.dump(new_member), 201)


@groups.route('/groups/<int:group_id>/members', methods=['GET'])
@jwt_required
def read_all_members(group_id):
    query = db.session.query(Member).filter_by(group_id=group_id)
    try:
        members = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    return logged_response(member_schema.dump(members, many=True))


@groups.route('/groups/<int:group_id>/members/<int:person_id>', methods=['GET'])
@jwt_required
def read_one_member(group_id, person_id):
    member = db.session.query(Member).filter_by(group_id=group_id, person_id=person_id).first()
    if member is None:
        return logged_response(f"Member with group_id #{group_id} and person_id #{person_id} does not exist", 404)
    return logged_response(member_schema.dump(member))


@groups.route('/groups/<int:group_id>/members/<int:person_id>', methods=['PATCH'])
@jwt_required
def update_member(group_id, person_id):
    member_schema = MemberSchema()
    try:
        valid_attributes = member_schema.load(request.json, partial=True)
    except ValidationError as err:
        return logged_response(err.messages, 422)

    member = db.session.query(Member).filter_by(group_id=group_id, person_id=person_id).first()
    if member is None:
        return logged_response(f"Member with group_id #{group_id} and person_id #{person_id} does not exist", 404)

    new_group_id = valid_attributes.get('group_id')
    new_person_id = valid_attributes.get('person_id')
    # if modifying member identity or belonging group
    if new_group_id or new_person_id:
        # check if entry already exists
        if db.session.query(Member).filter_by(
                person_id=new_person_id or person_id, 
                group_id=new_group_id or group_id).first():
            return logged_response(f"Member with group_id #{new_group_id} and person_id #{new_person_id} already exists", 409)
        # check if the new group exists
        if new_group_id and not db.session.query(Group).filter_by(id=new_group_id).first():
            return logged_response(f"Group with group_id #{new_group_id} does not exist", 404)
        # check if the new person exists
        if new_person_id and not db.session.query(Person).filter_by(id=new_person_id).first():
            return logged_response(f"Person with person_id #{new_person_id} does not exist", 404)

    for key, val in valid_attributes.items():
        setattr(member, key, val)

    db.session.add(member)
    db.session.commit()

    return logged_response(member_schema.dump(member), 200)


@groups.route('/groups/<int:group_id>/members/<int:person_id>', methods=['DELETE'])
@jwt_required
def delete_member(group_id, person_id):
    member = db.session.query(Member).filter_by(group_id=group_id, person_id=person_id).first()

    if member is None:
        return logged_response(f"Member with group_id #{group_id} and person_id #{person_id} does not exist", 404)

    db.session.delete(member)
    db.session.commit()

    return logged_response("Deleted successfully", 204)

# ---- Attendance

attendance_schema = AttendanceSchema()

@groups.route('/meetings/<int:meeting_id>/attendances/<int:person_id>', methods=['POST', 'PUT', 'PATCH'])
@jwt_required
def create_attendance(meeting_id, person_id):
    if not db.session.query(Person).filter_by(id=person_id).first():
        return logged_response(f"Person with person_id #{person_id} does not exist", 404)

    if not db.session.query(Meeting).filter_by(id=meeting_id).first():
        return logged_response(f"Meeting with meeting_id #{meeting_id} does not exist", 404)

    if db.session.query(Attendance).filter_by(person_id=person_id, meeting_id=meeting_id).first():
        # if the same attendance already exists
        return logged_response(f"Attendance with meeting_id #{meeting_id} and person_id #{person_id} already exists", 409)

    new_attendance = Attendance(meeting_id=meeting_id, person_id=person_id)
    db.session.add(new_attendance)
    db.session.commit()

    return logged_response(attendance_schema.dump(new_attendance), 201)

@groups.route('/meetings/<int:meeting_id>/attendances', methods=['GET'])
@jwt_required
def read_all_attendances(meeting_id):
    query = db.session.query(Attendance).filter_by(meeting_id=meeting_id)
    try:
        attendances = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return logged_response(e.message, e.code)
    return logged_response(attendance_schema.dump(attendances, many=True))

@groups.route('/meetings/<int:meeting_id>/attendances/<int:person_id>', methods=['DELETE'])
@jwt_required
def delete_attendance(meeting_id, person_id):
    attendance = db.session.query(Attendance).filter_by(meeting_id=meeting_id, person_id=person_id).first()

    if attendance is None:
        return logged_response(f"Attendance with meeting_id #{meeting_id} and person_id #{person_id} does not exist", 404)

    db.session.delete(attendance)
    db.session.commit()

    return logged_response("Deleted successfully", 204)

# ---- Image

@groups.route('/groups/<int:group_id>/images/<int:image_id>', methods=['POST'])
@jwt_required
def add_group_images(group_id, image_id):
    group = db.session.query(Group).filter_by(id=group_id).first()
    image = db.session.query(Image).filter_by(id=image_id).first()

    group_image = db.session.query(ImageGroup).filter_by(group_id=group_id, image_id=image_id).first()

    if not group:
        return logged_response(f"Group with id #{group_id} does not exist.", 404)

    if not image:
        return logged_response(f"Image with id #{image_id} does not exist.", 404)

    # If image is already attached to the group
    if group_image:
        return logged_response(f"Image with id#{image_id} is already attached to group with id#{group_id}.", 422)
    else:
        new_entry = ImageGroup(**{'group_id': group_id, 'image_id': image_id})
        db.session.add(new_entry)
        db.session.commit()

    return logged_response(f"Image with id #{image_id} successfully added to Group with id #{group_id}.", 201)


@groups.route('/groups/<int:group_id>/images/<int:image_id>', methods=['PUT'])
@jwt_required
def put_group_images(group_id, image_id):
    # check for old image id in parameter list (?old=<id>)
    old_image_id = request.args['old']
    new_image_id = image_id

    if old_image_id == 'false':
        post_resp = add_group_images(group_id, new_image_id)
        return logged_response({'deleted': 'No image to delete', 'posted': str(post_resp[0].data, "utf-8")})
    else:
        del_resp = delete_group_image(group_id, old_image_id)
        post_resp = add_group_images(group_id, new_image_id)

        return logged_response({'deleted': del_resp[0], 'posted': str(post_resp[0].data, "utf-8")})


@groups.route('/groups/<int:group_id>/images/<int:image_id>', methods=['DELETE'])
@jwt_required
def delete_group_image(group_id, image_id):
    group_image = db.session.query(ImageGroup).filter_by(group_id=group_id, image_id=image_id).first()

    if not group_image:
        return logged_response(f"Image with id #{image_id} is not assigned to Group with id #{group_id}.", 404)

    db.session.delete(group_image)
    db.session.commit()

    # 204 codes don't respond with any content
    return logged_response('Successfully removed image', 204)

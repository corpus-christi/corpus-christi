import json

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from marshmallow import ValidationError
from ..auth.utils import jwt_not_required
from . import people
from .models import func, Person, Account, AccountSchema, Role, PersonSchema, \
    RoleSchema, Manager, ManagerSchema
from ..events.models import EventPerson, EventParticipant
from ..teams.models import TeamMember
from ..attributes.models import Attribute, AttributeSchema, EnumeratedValue, \
    EnumeratedValueSchema, PersonAttribute, PersonAttributeSchema
from ..images.models import Image, ImageSchema, ImagePerson, ImagePersonSchema
from ..courses.models import Student, ClassMeeting
from ..auth.blacklist_helpers import revoke_tokens_of_account

from .. import db

# ---- Person

person_schema = PersonSchema()
person_attribute_schema = PersonAttributeSchema()
attribute_schema = AttributeSchema(exclude=['active'])
enumerated_value_schema = EnumeratedValueSchema(exclude=['active'])


@people.route('/persons/fields', methods=['GET'])
def read_person_fields():
    response = {'person': [], 'person_attributes': []}

    person_columns = Person.__table__.columns
    attributes = db.session.query(Attribute).filter_by(active=True).all()
    enumerated_values = db.session.query(
        EnumeratedValue).filter_by(active=True).all()
    attributes = attribute_schema.dump(attributes, many=True)
    enumerated_values = enumerated_value_schema.dump(
        enumerated_values, many=True)

    for c in person_columns:
        response['person'].append(
            {c.name: str(c.type), 'required': not c.nullable})

    for a in attributes:
        a[a['nameI18n']] = [x for x in enumerated_values if x['attributeId'] == a['id']]
        response['person_attributes'].append(a)

    return jsonify(response)


@people.route('/persons', methods=['POST'])
def create_person():
    request.json['person']['active'] = True

    for key, value in request.json['person'].items():
        if request.json['person'][key] is "" or request.json['person'][key] is 0:
            request.json['person'][key] = None

    try:
        valid_person = person_schema.load(request.json['person'])
        valid_person_attributes = person_attribute_schema.load(
            request.json['attributesInfo'], many=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_person = Person(**valid_person)
    db.session.add(new_person)
    db.session.commit()

    for person_attribute in valid_person_attributes:
        if (person_attribute['enum_value_id'] is 0):
            person_attribute['enum_value_id'] = None
        person_attribute = PersonAttribute(**person_attribute)
        person_attribute.person_id = new_person.id
        db.session.add(person_attribute)

    db.session.commit()
    result = db.session.query(Person).filter_by(id=new_person.id).first()
    result.attributesInfo = result.person_attributes

    return jsonify(person_schema.dump(result)), 201


@people.route('/persons')
@jwt_required
def read_all_persons():
    result = db.session.query(Person).all()
    for r in result:
        r.attributesInfo = r.person_attributes
        r.accountInfo = r.account
        if r.account:
            r.accountInfo.roles = r.account.roles

    return jsonify(person_schema.dump(result, many=True))


@people.route('/persons/<person_id>')
@jwt_required
def read_one_person(person_id):
    result = db.session.query(Person).filter_by(id=person_id).first()
    if result is None:
        return 'Person specified was NOT found', 404
    result.attributesInfo = result.person_attributes
    result.accountInfo = result.account
    return jsonify(person_schema.dump(result))


@people.route('/persons/<person_id>', methods=['PUT'])
@jwt_required
def update_person(person_id):
    try:
        valid_person = person_schema.load(request.json['person'], partial=True)
        valid_person_attributes = person_attribute_schema.load(
            request.json['attributesInfo'], many=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
    for new_person_attribute in valid_person_attributes:
        old_person_attribute = db.session.query(PersonAttribute).filter_by(
            person_id=person_id, attribute_id=new_person_attribute['attribute_id']).first()
        if old_person_attribute is not None:
            value = None
            if 'string_value' in new_person_attribute:
                value = new_person_attribute['string_value']
            setattr(old_person_attribute, 'string_value',
                    value)
            value = None
            if 'enum_value_id' in new_person_attribute:
                value = new_person_attribute['enum_value_id']
            setattr(old_person_attribute, 'enum_value_id',
                    value)
        else:
            new_person_attribute = PersonAttribute(**new_person_attribute)
            new_person_attribute.person_id = person_id
            db.session.add(new_person_attribute)

    person = db.session.query(Person).filter_by(id=person_id).first()
    if person is None:
        return 'Person specified was NOT found', 404

    if person is None:
        return jsonify("Person does not exist"), 404

    for key, val in valid_person.items():
        setattr(person, key, val)

    db.session.commit()

    result = db.session.query(Person).filter_by(id=person_id).first()
    result.attributesInfo = result.person_attributes
    return jsonify(person_schema.dump(result))


@people.route('/persons/deactivate/<person_id>', methods=['PUT'])
@jwt_required
def deactivate_person(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()
    if person is None:
        return 'Person specified was NOT found', 404

    if person.account:
        account = db.session.query(Account).filter_by(
            id=person.account.id).first()
        if account is None:
            return 'Account specified was NOT found', 404
        setattr(account, 'active', False)
    setattr(person, 'active', False)

    db.session.commit()

    return jsonify(person_schema.dump(person))


@people.route('/persons/activate/<person_id>', methods=['PUT'])
@jwt_required
def activate_person(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()
    if person is None:
        return jsonify("person does not exist"), 404
    setattr(person, 'active', True)

    db.session.commit()

    return jsonify(person_schema.dump(person))


@people.route('/persons/delete/<person_id>', methods=['DELETE'])
@jwt_required
def delete_person(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()

    if person is None:
        return jsonify(msg="Person not found"), 404

    db.session.query(TeamMember).filter_by(member_id=person_id).delete()
    db.session.query(EventParticipant).filter_by(person_id=person_id).delete()
    db.session.query(EventPerson).filter_by(person_id=person_id).delete()
    db.session.query(Student).filter_by(student_id=person_id).delete()
    db.session.query(Account).filter_by(person_id=person_id).delete()
    db.session.query(PersonAttribute).filter_by(person_id=person_id).delete()
    # TODO delete any instance of Class_Attendance that references deleted class_meeting
    # db.session.query(ClassMeeting).filter_by(teacher=person_id).delete()
    db.session.delete(person)
    db.session.commit()
    return jsonify(msg=f"Person {person_id} was deleted."), 204


# ---- Account

account_schema = AccountSchema()


@people.route('/accounts', methods=['POST'])
def create_account():
    request.json["active"] = True
    try:
        valid_account = account_schema.load(request.json)
    except ValidationError as err:
        print("ERR", err)
        return jsonify(err.messages), 422

    public_user_role = db.session.query(Role).filter_by(id=1).first()

    new_account = Account(**valid_account)
    new_account.active = True
    new_account.roles.append(public_user_role)
    db.session.add(new_account)
    db.session.commit()
    return jsonify(account_schema.dump(new_account)), 201


@people.route('/accounts')
@jwt_required
def read_all_accounts():
    result = db.session.query(Account).all()
    return jsonify(account_schema.dump(result, many=True))


@people.route('/accounts/<account_id>')
@jwt_required
def read_one_account(account_id):
    """Read one account by ID."""
    result = db.session.query(Account).filter_by(id=account_id).first()
    if result is None:
        return 'Account specified was NOT found', 404
    return jsonify(account_schema.dump(result))


@people.route('/accounts/username/<username>')
@jwt_required
def read_one_account_by_username(username):
    """Read one account by its (unique) user name."""
    result = db.session.query(Account).filter_by(username=username).first()
    if result is None:
        return 'Account specified was NOT found', 404
    return jsonify(account_schema.dump(result))


@people.route('/persons/<person_id>/account')
@jwt_required
def read_person_account(person_id):
    account = db.session.query(Account).filter_by(person_id=person_id).first()
    if account is None:
        return 'Account specified was NOT found', 404
    return jsonify(account_schema.dump(account))


@people.route('/role/<role_id>/accounts')
@jwt_required
def get_accounts_by_role(role_id):
    role = db.session.query(Role).filter_by(id=role_id).first()
    if role is None:
        return 'Role specified was NOT found', 404
    return jsonify(account_schema.dump(role.accounts, many=True))


@people.route('/accounts/<account_id>', methods=['PATCH'])
@jwt_required
def update_account(account_id):
    try:
        account_request = request.json.copy()
        account_request.pop('roles', None)
        account_schema.load(account_request, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'Account specified was NOT found', 404

    roles_to_add = []
    if 'roles' in request.json:
        roles_to_add = request.json['roles']

    # Only these fields can be meaningfully updated.
    for field in 'password', 'username', 'active':
        if field in request.json:
            setattr(account, field, request.json[field])

    if roles_to_add is not None:
        role_objects = []
        for role in roles_to_add:
            role_object = db.session.query(Role).filter_by(id=role).first()
            role_objects.append(role_object)
        revoke_tokens_of_account(account.id)

    account.roles = role_objects

    db.session.commit()
    return jsonify(account_schema.dump(account))


@people.route('/accounts/deactivate/<account_id>', methods=['PUT'])
@jwt_required
def deactivate_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'Account specified was NOT found', 404

    setattr(account, 'active', False)

    db.session.commit()

    return jsonify(account_schema.dump(account))


@people.route('/accounts/activate/<account_id>', methods=['PUT'])
@jwt_required
def activate_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'Account specified was NOT found', 404

    setattr(account, 'active', True)

    db.session.commit()

    return jsonify(account_schema.dump(account))


@people.route('/accounts/<account_id>/confirm')
@jwt_required
# @authorize(['role.superuser, role.infrastructure']) # <-- Only these people can confirm an account
def confirm_user_account(account_id):
    """ Confirm a user's account (ADMIN ACTION ONLY) """
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'Account to confirm was NOT found', 404

    setattr(account, 'confirmed', True)

    db.session.commit()

    return jsonify(account_schema.dump(account))


# ---- Roles


role_schema = RoleSchema()


@people.route('/role', methods=['POST'])
@jwt_required
def create_role():
    try:
        valid_role = role_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_role = Role(**valid_role)
    db.session.add(new_role)
    db.session.commit()
    return jsonify(role_schema.dump(new_role)), 201


@people.route('/role')
@jwt_required
def read_all_roles():
    result = db.session.query(Role).all()
    return jsonify(role_schema.dump(result, many=True))


@people.route('/role/account/<account_id>')
@jwt_required
def get_roles_for_account(account_id):
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return jsonify("accounts does not exist"), 404
    result = []
    for role in account.roles:
        role = role_schema.dump(role)
        result.append(role["nameI18n"])
    return jsonify(result)


@people.route('/role/<role_id>')
@jwt_required
def read_one_role(role_id):
    result = db.session.query(Role).filter_by(id=role_id).first()
    if result is None:
        return jsonify("Role does not exist"), 404
    return jsonify(role_schema.dump(result))


@people.route('/role/<role_id>', methods=['PATCH'])
@jwt_required
def update_role(role_id):
    try:
        valid_role = role_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    role = db.session.query(Role).filter_by(id=role_id).first()
    if role is None:
        return 'Role specified was NOT found', 404

    if role is None:
        return jsonify("Role does not exist"), 404

    for key, val in valid_role.items():
        setattr(role, key, val)

    db.session.commit()
    return jsonify(role_schema.dump(role))


@people.route('/role/activate/<role_id>', methods=['PUT'])
@jwt_required
def activate_role(role_id):
    role = db.session.query(Role).filter_by(id=role_id).first()
    setattr(role, 'active', True)
    db.session.commit()
    return jsonify(role_schema.dump(role))


@people.route('/role/deactivate/<role_id>', methods=['PUT'])
@jwt_required
def deactivate_role(role_id):
    role = db.session.query(Role).filter_by(id=role_id).first()

    setattr(role, 'active', False)

    db.session.commit()

    return jsonify(role_schema.dump(role))


@people.route('/role/<account_id>&<role_id>', methods=['POST'])
@jwt_required
def add_role_to_account(account_id, role_id):
    account = db.session.query(Account).filter_by(id=account_id).first()

    if account is None:
        return 'Account not found', 404

    role_to_add = db.session.query(Role).filter_by(id=role_id).first()

    account.roles.append(role_to_add)
    db.session.add(account)
    db.session.commit()

    revoke_tokens_of_account(account.id)

    user_roles = []
    roles = db.session.query(Role).join(Account, Role.accounts).filter_by(
        id=account_id).filter_by(active=True).all()
    for r in roles:
        user_roles.append(role_schema.dump(r)['nameI18n'])

    return jsonify(user_roles)


@people.route('/role/<account_id>&<role_id>', methods=['DELETE'])
@jwt_required
def remove_role_from_account(account_id, role_id):
    account = db.session.query(Account).filter_by(id=account_id).first()
    if account is None:
        return 'Account not found', 404

    role_to_remove = db.session.query(Role).filter_by(id=role_id).first()
    if role_to_remove is None:
        return 'Role specified was NOT found', 404

    if role_to_remove not in account.roles:
        return 'That account does not have that role', 404

    account.roles.remove(role_to_remove)
    db.session.commit()
    revoke_tokens_of_account(account_id)

    # user_roles = []
    # roles = db.session.query(Role).join(Account, Role.accounts).filter_by(id=account_id).filter_by(active=True).all()
    # for r in roles:
    #     user_roles.append(role_schema.dump(r)['nameI18n'])
    #
    # return jsonify(user_roles)
    return jsonify(role_schema.dump(role_to_remove))


# ---- Manager

manager_schema = ManagerSchema()


@people.route('/manager', methods=['POST'])
@jwt_required
def create_manager():
    try:
        valid_manager = manager_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_manager = Manager(**valid_manager)
    db.session.add(new_manager)
    db.session.commit()
    return jsonify(manager_schema.dump(new_manager)), 201


@people.route('/manager')
@jwt_required
def read_all_managers():
    show_unique_persons_only = request.args.get('show_unique_persons_only')

    # Remove duplicate persons
    if show_unique_persons_only == 'Y':
        result = db.session.query(Manager).distinct(Manager.person_id).all()
    else:
        result = db.session.query(Manager)

    return jsonify(manager_schema.dump(result, many=True))


@people.route('/manager/<manager_id>')
@jwt_required
def read_one_manager(manager_id):
    result = db.session.query(Manager).filter_by(id=manager_id).first()
    if result is None:
        return jsonify("Manager does not exist"), 404
    return jsonify(manager_schema.dump(result))


@people.route('/manager/<manager_id>', methods=['PATCH'])
@jwt_required
def update_manager(manager_id):
    try:
        valid_manager = manager_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    manager = db.session.query(Manager).filter_by(id=manager_id).first()

    for key, val in valid_manager.items():
        setattr(manager, key, val)

    db.session.commit()
    return jsonify(manager_schema.dump(manager))


@people.route('/manager/<manager_id>', methods=['DELETE'])
@jwt_required
def delete_manager(manager_id):
    manager = db.session.query(Manager).filter_by(id=manager_id).first()

    if manager is None:
        return 'Manager not found', 404

    for subordinate in manager.subordinates:
        setattr(subordinate, 'manager_id', None)

    db.session.delete(manager)
    db.session.commit()

    return jsonify(manager_schema.dump(manager)), 204


# ---- Image

@people.route('/<person_id>/images/<image_id>', methods=['POST'])
@jwt_required
def add_people_images(person_id, image_id):
    person = db.session.query(Person).filter_by(id=person_id).first()
    image = db.session.query(Image).filter_by(id=image_id).first()

    person_image = db.session.query(ImagePerson).filter_by(person_id=person_id, image_id=image_id).first()

    if not person:
        return jsonify(f"Person with id #{person_id} does not exist."), 404

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    # If image is already attached to the person
    if person_image:
        return jsonify(f"Image with id#{image_id} is already attached to person with id#{person_id}."), 422
    else:
        new_entry = ImagePerson(
            **{'person_id': person_id, 'image_id': image_id})
        db.session.add(new_entry)
        db.session.commit()

    return jsonify(f"Image with id #{image_id} successfully added to Person with id #{person_id}."), 201


@people.route('/<person_id>/images/<image_id>', methods=['PUT'])
@jwt_required
def put_people_images(person_id, image_id):
    # check for old image id in parameter list (?old=<id>)
    old_image_id = request.args['old']
    new_image_id = image_id

    if old_image_id == 'false':
        post_resp = add_people_images(person_id, new_image_id)
        return jsonify({'deleted': 'No image to delete', 'posted': str(post_resp[0].data, "utf-8")})
    else:
        del_resp = delete_person_image(person_id, old_image_id)
        post_resp = add_people_images(person_id, new_image_id)

        return jsonify({'deleted': del_resp[0], 'posted': str(post_resp[0].data, "utf-8")})


@people.route('/<person_id>/images/<image_id>', methods=['DELETE'])
@jwt_required
def delete_person_image(person_id, image_id):
    person_image = db.session.query(ImagePerson).filter_by(
        person_id=person_id, image_id=image_id).first()

    if not person_image:
        return jsonify(f"Image with id #{image_id} is not assigned to Person with id #{person_id}."), 404

    db.session.delete(person_image)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed image', 204

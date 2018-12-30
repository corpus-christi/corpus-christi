from flask import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import roles
from .models import RoleSchema, Role
from .. import db

# ---- Role

role_schema = RoleSchema()


@roles.route('/roles', methods=['POST'])
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


@roles.route('/roles')
@jwt_required
def read_all_roles():
    result = db.session.query(Role).all()
    return jsonify(role_schema.dump(result, many=True))

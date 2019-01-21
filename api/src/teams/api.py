import json
from datetime import datetime, timedelta

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from ..people.models import Person, PersonSchema
from .models import Team, TeamMember, TeamSchema, TeamMemberSchema
from . import teams
from .. import db
from ..etc.helper import modify_entity, get_exclusion_list

# ---- Team

@teams.route('/', methods=['POST'])
@jwt_required
def create_team():
    team_schema = TeamSchema(exclude=get_exclusion_list(request.args, ['members', 'events']))
    try:
        valid_team = team_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_team = Team(**valid_team)
    db.session.add(new_team)
    db.session.commit()
    return jsonify(team_schema.dump(new_team)), 201
    

@teams.route('/')
@jwt_required
def read_all_teams():
    team_schema = TeamSchema(exclude=get_exclusion_list(request.args, ['members', 'events']))
    query = db.session.query(Team)

    # -- return_inactives --
    # Filter assets based on active status
    return_group = request.args.get('return_group')
    if return_group == 'inactive':
        query = query.filter_by(active=False)
    elif return_group in ('all', 'both'):
        pass # Don't filter
    else:
        query = query.filter_by(active=True)

    # -- description --
    # Filter events on a wildcard description string
    desc_filter = request.args.get('desc')
    if desc_filter:
        query = query.filter(Team.description.like(f"%{desc_filter}%"))

    # Sorting
    sort_filter = request.args.get('sort')
    if sort_filter:
        sort_column = None
        if sort_filter[:11] == 'description':
            sort_column = Team.description

        if sort_filter[-4:] == 'desc' and sort_column:
            sort_column = sort_column.desc()
        
        query = query.order_by(sort_column)

    result = query.all()
    return jsonify(team_schema.dump(result, many=True))
    

@teams.route('/<team_id>')
@jwt_required
def read_one_team(team_id):
    team_schema = TeamSchema(exclude=get_exclusion_list(request.args, ['members', 'events']))
    team = db.session.query(Team).filter_by(id=team_id).first()

    if not team:
        return jsonify(f"Team with id #{team_id} does not exist."), 404

    return jsonify(team_schema.dump(team))


@teams.route('/members')
@jwt_required
def read_all_team_members():
    team_schema = TeamSchema(exclude=['members', 'events'])
    person_schema = PersonSchema()
    teams = db.session.query(Team).all()

    constructed_dict = dict()
    for team in teams:
        for member in team.members:
            member_id = member.member_id
            if member_id not in constructed_dict:
                constructed_dict[member_id] = person_schema.dump(member.member)
                constructed_dict[member_id]['active'] = member.active
                constructed_dict[member_id]['teams'] = list()
            constructed_dict[member_id]['teams'].append(team_schema.dump(team))

    return jsonify(constructed_dict)


@teams.route('/<team_id>', methods=['PUT'])
@jwt_required
def replace_team(team_id):
    team_schema = TeamSchema(exclude=get_exclusion_list(request.args, ['members', 'events']))
    try:
        valid_team = team_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_entity(Team, team_schema, team_id, valid_team)
    

@teams.route('/<team_id>', methods=['PATCH'])
@jwt_required
def update_team(team_id):
    team_schema = TeamSchema(exclude=get_exclusion_list(request.args, ['members', 'events']))
    try: 
        valid_attributes = team_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_entity(Team, team_schema, team_id, valid_attributes)
    

@teams.route('/<team_id>', methods=['DELETE'])
@jwt_required
def delete_team(team_id):
    team = db.session.query(Team).filter_by(id=team_id).first()

    if not team:
        return jsonify(f"Team with id #{team_id} does not exist."), 404
        
    setattr(team, 'active', False)
    db.session.commit()
    
    # 204 codes don't respond with any content
    return 'Successfully deleted team', 204

@teams.route('/<team_id>/members')
@jwt_required
def get_team_members(team_id):
    team_member_schema = TeamMemberSchema(exclude=get_exclusion_list(request.args, ['team']))
    team_members = db.session.query(TeamMember).filter_by(team_id=team_id).all()

    if not team_members:
        return jsonify(f"Team with id #{team_id} does not have any members."), 404

    return jsonify(team_member_schema.dump(team_members, many=True))

@teams.route('/<team_id>/members/<member_id>', methods=['PATCH'])
@jwt_required
def modify_team_member(team_id, member_id):
    team_member_schema = TeamMemberSchema(exclude=get_exclusion_list(request.args, ['team']))
    try:
        valid_attributes = team_member_schema.load(request.json, partial=('team_id', 'member_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    team_member = db.session.query(TeamMember).filter_by(member_id=member_id).filter_by(team_id=team_id).first()

    if not team_member:
        return jsonify(f"Member with id #{member_id} is not associated with Team with id #{team_id}."), 404

    setattr(team_member, 'active', valid_attributes['active'])
    db.session.commit()

    return jsonify(team_member_schema.dump(team_member))

@teams.route('/<team_id>/members/<member_id>', methods=['POST','PUT'])
@jwt_required
def add_team_member(team_id, member_id):
    team_member_schema = TeamMemberSchema(exclude=get_exclusion_list(request.args, ['team']))
    try:
        valid_attributes = team_member_schema.load(request.json, partial=('team_id', 'member_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    team = db.session.query(Team).filter_by(id=team_id).first()
    person = db.session.query(Person).filter_by(id=member_id).first()

    if not team:
        return jsonify(f"Team with id #{team_id} does not exist."), 404
    if not person:
        return jsonify(f"Person with id #{member_id} does not exist."), 404

    team_member = db.session.query(TeamMember).filter_by(team_id=team_id,member_id=member_id).first()

    if not team_member:
        new_entry = TeamMember(**{'team_id': team_id, 'member_id': member_id, 'active': valid_attributes['active']})
        db.session.add(new_entry)
        db.session.commit()
        return 'Team member successfully added.'
    else:
        return jsonify(f"Person with id #{member_id} is already on Team with id #{team_id}."), 422

@teams.route('/<team_id>/members/<member_id>', methods=['DELETE'])
@jwt_required
def delete_team_member(team_id, member_id):
    team_member = db.session.query(TeamMember).filter_by(team_id=team_id).filter_by(member_id=member_id).first()

    if not team_member:
        return jsonify(f"Member with id #{member_id} is not on Team with id #{team_id}."), 404

    if not team_member.active:
        return jsonify(f"Member with id #{member_id} is already set as INACTIVE on Team with id #{team_id}."), 422

    setattr(team_member, 'active', False)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed team member', 204

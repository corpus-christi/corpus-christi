import json
from datetime import datetime, timedelta

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from . import events
from .models import Event, Asset, Team, TeamMember, EventPerson, EventAsset, EventParticipant, EventTeam, EventSchema, AssetSchema, TeamSchema, TeamMemberSchema, EventTeamSchema, EventPersonSchema, EventParticipantSchema, EmailSchema
from ..people.models import Person, PersonSchema
from .. import db, mail

def modify_entity(entity_type, schema, id, new_value_dict):
    item = db.session.query(entity_type).filter_by(id=id).first()

    if not item:
        return jsonify(f"Item with id #{id} does not exist."), 404

    for key, val in new_value_dict.items():
        if key != 'id':
            setattr(item, key, val)
    
    db.session.commit()

    return jsonify(schema.dump(item)), 200

def get_exclusion_list(query_object, default_exclusion_list):
    for exclusion in default_exclusion_list:
        include_filter = request.args.get(f"include_{exclusion}")
        if include_filter:
            default_exclusion_list.remove(exclusion)
    return default_exclusion_list

# ---- Event

@events.route('/', methods=['POST'])
@jwt_required
def create_event():
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams']))
    try:
        valid_event = event_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_event = Event(**valid_event)
    db.session.add(new_event)
    db.session.commit()
    return jsonify(event_schema.dump(new_event)), 201
    

@events.route('/')
@jwt_optional
def read_all_events():
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams']))
    query = db.session.query(Event)

    # -- return_inactives --
    # Filter events based on active status
    # True - see all events, False or missing - see only active events
    return_group = request.args.get('return_group')
    if return_group == 'inactive':
        query = query.filter_by(active=False)
    elif return_group in ('all', 'both'):
        pass # Don't filter
    else:
        query = query.filter_by(active=True)

    # -- start, end --
    # Filter events to be greater than the start date and/or earlier than the end date (inclusive)
    start_filter = request.args.get('start')
    end_filter = request.args.get('end')
    if start_filter:
        query = query.filter(Event.start > (datetime.strptime(start_filter, '%Y-%m-%d') - timedelta(days=1)))
    if end_filter:
        query = query.filter(Event.end < (datetime.strptime(end_filter, '%Y-%m-%d') + timedelta(days=1)))

    # -- title --
    # Filter events on a wildcard title string
    title_filter = request.args.get('title')
    if title_filter:
        query = query.filter(Event.title.like(f"%{title_filter}%"))

    # -- location --
    # Filter events on a wildcard location string?
    location_filter = request.args.get('location_id')
    if location_filter:
        query = query.filter_by(location_id=location_filter)

    result = query.all()

    return jsonify(event_schema.dump(result, many=True))
    

@events.route('/<event_id>')
@jwt_required
def read_one_event(event_id):
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams']))
    event = db.session.query(Event).filter_by(id=event_id).first()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    return jsonify(event_schema.dump(event))
    

@events.route('/<event_id>', methods=['PUT'])
@jwt_required
def replace_event(event_id):
    event_schema = EventSchema()
    try:
        valid_event = event_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams']))

    return modify_entity(Event, event_schema, event_id, valid_event)


@events.route('/<event_id>', methods=['PATCH'])
@jwt_required
def update_event(event_id):
    event_schema = EventSchema()
    try: 
        valid_attributes = event_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams']))
                
    return modify_entity(Event, event_schema, event_id, valid_attributes)


@events.route('/<event_id>', methods=['DELETE'])
@jwt_required
def delete_event(event_id):
    event = db.session.query(Event).filter_by(id=event_id).first()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404
        
    setattr(event, 'active', False)
    db.session.commit()
    
    # 204 codes don't respond with any content
    return "Deleted successfully", 204


@events.route('/<event_id>/assets/<asset_id>', methods=['POST', 'PUT', 'PATCH'])
@jwt_required
def add_asset_to_event(event_id, asset_id):
    event = db.session.query(Event).filter_by(id=event_id).first()
    asset_events = db.session.query(Event).join(EventAsset).filter_by(asset_id=asset_id).all()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    # Make sure asset isn't already booked in the current event
    # Make sure asset isn't booked in another event during that time 
    for asset_event in asset_events:
        if event.start <= asset_event.start < event.end \
        or asset_event.start <= event.start < asset_event.end \
        or event.start < asset_event.end <= event.end \
        or asset_event.start < event.end <= asset_event.end:
            return jsonify(f"Asset with id #{asset_id} is unavailable for Event with id #{event_id}."), 422

    new_entry = EventAsset(**{'event_id': event_id, 'asset_id': asset_id})
    db.session.add(new_entry)
    db.session.commit()

    return jsonify(f"Asset with id #{asset_id} successfully booked for Event with id #{event_id}.")

@events.route('/<event_id>/assets/<asset_id>', methods=['DELETE'])
@jwt_required
def remove_asset_from_event(event_id, asset_id):
    event_asset = db.session.query(EventAsset).filter_by(event_id=event_id).filter_by(asset_id=asset_id).first()

    if not event_asset:
        return jsonify(f"Asset with id #{asset_id} is not booked for Event with id #{event_id}."), 404

    db.session.delete(event_asset)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully un-booked', 204

@events.route('/<event_id>/teams')
@jwt_required
def get_event_teams(event_id):
    teams = db.session.query(Team).join(EventTeam).filter_by(event_id=event_id).all()

    return jsonify(team_schema.dump(teams, many=True))

@events.route('/<event_id>/teams/<team_id>', methods=['POST','PUT','PATCH'])
@jwt_required
def add_event_team(event_id, team_id):
    event = db.session.query(Event).filter_by(id=event_id).first()
    event_teams = db.session.query(Event).join(EventTeam).filter_by(team_id=team_id).all()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    # Make sure asset isn't already booked in the current event
    # Make sure asset isn't booked in another event during that time
    event_start = event.start
    event_end = event.end

    is_overlap = False

    for event_team in event_teams:
        if event_start <= event_team.start < event_end or event_start < event_team.end <= event_end \
          or event_team.start <= event_start < event_team.end or event_team.start < event.end <= event_team.end:
            is_overlap = True
            break

    if is_overlap:
        return jsonify(f"Team with id #{team_id} is unavailable for Event with id #{event_id}."), 422
    else:
        new_entry = EventTeam(**{'event_id': event_id, 'team_id': team_id})
        db.session.add(new_entry)
        db.session.commit()

        return jsonify(f"Team with id #{team_id} successfully booked for Event with id #{event_id}.")

@events.route('/<event_id>/teams/<team_id>', methods=['DELETE'])
@jwt_required
def delete_event_team(event_id, team_id):
    event_team = db.session.query(EventTeam).filter_by(team_id=team_id).filter_by(event_id=event_id).first()

    if not event_team:
        return jsonify(f"Team with id #{team_id} is not assigned to Event with id #{event_id}."), 404

    db.session.delete(event_team)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed team member', 204

event_person_schema = EventPersonSchema(exclude=['event'])

@events.route('/<event_id>/individuals')
@jwt_required
def get_event_persons(event_id):
    people = db.session.query(EventPerson).filter_by(event_id=event_id).all()

    return jsonify(event_person_schema.dump(people, many=True))

@events.route('/<event_id>/individuals/<person_id>', methods=['POST','PUT'])
@jwt_required
def add_event_persons(event_id, person_id):
    try:
        valid_description = event_person_schema.load(request.json, partial=('event_id', 'person_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    event = db.session.query(Event).filter_by(id=event_id).first()
    event_people = db.session.query(Event).join(EventPerson).filter_by(person_id=person_id).all()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    # Make sure individual isn't already booked in the current event
    # Make sure individual isn't booked in another event during that time
    event_start = event.start
    event_end = event.end

    is_overlap = False

    for event_person in event_people:
        if event_start <= event_person.start < event_end or event_start < event_person.end <= event_end \
          or event_person.start <= event_start < event_person.end or event_person.start < event.end <= event_person.end:
            is_overlap = True
            break

    if is_overlap:
        return jsonify(f"Person with id #{person_id} is unavailable for Event with id #{event_id}."), 422
    else:
        new_entry = EventPerson(**{'event_id': event_id, 'person_id': person_id, 'description': valid_description['description']})
        db.session.add(new_entry)
        db.session.commit()

        return jsonify(f"Person with id #{person_id} successfully booked for Event with id #{event_id}.")

@events.route('/<event_id>/individuals/<person_id>', methods=['PATCH'])
@jwt_required
def modify_event_person(event_id, person_id):
    try:
        valid_description = event_person_schema.load(request.json, partial=('event_id', 'person_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    event_person = db.session.query(EventPerson).filter_by(person_id=person_id).filter_by(event_id=event_id).first()

    if not event_person:
        return jsonify(f"Person with id #{person_id} is not associated with Event with id #{event_id}."), 404

    setattr(event_person, 'description', valid_description['description'])
    db.session.commit()

    return jsonify(event_person_schema.dump(event_person))

@events.route('/<event_id>/individuals/<person_id>', methods=['DELETE'])
@jwt_required
def delete_event_persons(event_id, person_id):
    event_person = db.session.query(EventPerson).filter_by(person_id=person_id).filter_by(event_id=event_id).first()

    if not event_person:
        return jsonify(f"Person with id #{person_id} is not assigned to Event with id #{event_id}."), 404

    db.session.delete(event_person)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed individual', 204

# ---- Participant

event_participant_schema = EventParticipantSchema(exclude=['event'])

@events.route('/<event_id>/participants')
@jwt_required
def get_event_participants(event_id):
    participants = db.session.query(EventParticipant).filter_by(event_id=event_id).all()

    return jsonify(event_participant_schema.dump(participants, many=True))

@events.route('/<event_id>/participants/<person_id>', methods=['POST','PUT'])
@jwt_required
def add_event_participants(event_id, person_id):
    try:
        valid_confirmation = event_participant_schema.load(request.json, partial=('event_id', 'person_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    event = db.session.query(Event).filter_by(id=event_id).first()
    event_participants = db.session.query(Event).join(EventParticipant).filter_by(person_id=person_id).all()

    event_participant = db.session.query(EventParticipant).filter_by(event_id=event_id,person_id=person_id).first()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    # If participant is already booked for the event
    if event_participant:
        return jsonify(f"Person with id#{person_id} is already booked for event with id#{event_id}."), 422
    else:
        new_entry = EventParticipant(**{'event_id': event_id, 'person_id': person_id, 'confirmed': valid_confirmation['confirmed']})
        db.session.add(new_entry)
        db.session.commit()

    return jsonify(f"Person with id #{person_id} successfully booked for Event with id #{event_id}.")

@events.route('/<event_id>/participants/<person_id>', methods=['PATCH'])
@jwt_required
def modify_event_participant(event_id, person_id):
    try:
        valid_confirmation = event_participant_schema.load(request.json, partial=('event_id', 'person_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    event_participant = db.session.query(EventParticipant).filter_by(person_id=person_id).filter_by(event_id=event_id).first()

    if not event_participant:
        return jsonify(f"Person with id #{person_id} is not associated with Event with id #{event_id}."), 404

    setattr(event_participant, 'confirmed', valid_confirmation['confirmed'])
    db.session.commit()

    return jsonify(event_person_schema.dump(event_participant))

@events.route('/<event_id>/participants/<person_id>', methods=['DELETE'])
@jwt_required
def delete_event_participant(event_id, person_id):
    event_participant = db.session.query(EventParticipant).filter_by(person_id=person_id).filter_by(event_id=event_id).first()

    if not event_participant:
        return jsonify(f"Person with id #{person_id} is not assigned to Event with id #{event_id}."), 404

    db.session.delete(event_participant)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed participant', 204

# ---- Asset

asset_schema = AssetSchema()

@events.route('/assets', methods=['POST'])
@jwt_required
def create_asset():
    try:
        valid_asset = asset_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_asset = Asset(**valid_asset)
    db.session.add(new_asset)
    db.session.commit()
    return jsonify(asset_schema.dump(new_asset)), 201
    

@events.route('/assets')
@jwt_required
def read_all_assets():

    query = db.session.query(Asset).add_columns(func.count(EventAsset.event_id).label('event_count'))

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
        query = query.filter(Asset.description.like(f"%{desc_filter}%"))

    # -- location --
    # Filter events on a wildcard location string?
    location_filter = request.args.get('location')
    if location_filter:
        # TODO FIXME
        pass

    result = query.join(EventAsset, isouter=True).group_by(Asset.id).all()

    temp_result = list()
    for item in result:
        temp_result.append(asset_schema.dump(item[0]))
        temp_result[-1]['event_count'] = item[1]

    return jsonify(asset_schema.dump(temp_result, many=True))

@events.route('/assets/<asset_id>')
@jwt_required
def read_one_asset(asset_id):
    asset = db.session.query(Asset).filter_by(id=asset_id).add_columns(func.count(EventAsset.event_id).label('event_count')).join(EventAsset, isouter=True).group_by(Asset.id).first()
    
    if not asset:
        return jsonify(f"Asset with id #{asset_id} does not exist."), 404

    result = asset_schema.dump(asset[0])
    result['event_count'] = asset[1]

    return jsonify(asset_schema.dump(result))


@events.route('/assets/<asset_id>', methods=['PUT'])
@jwt_required
def replace_asset(asset_id):
    try:
        valid_asset = asset_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_asset(asset_id, valid_asset)
    

@events.route('/assets/<asset_id>', methods=['PATCH'])
@jwt_required
def update_asset(asset_id):
    try: 
        valid_attributes = asset_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_asset(asset_id, valid_attributes)
    

@events.route('/assets/<asset_id>', methods=['DELETE'])
@jwt_required
def delete_asset(asset_id):
    asset = db.session.query(Asset).filter_by(id=asset_id).first()

    if not asset:
        return jsonify(f"Event with id #{asset_id} does not exist."), 404
        
    setattr(asset, 'active', False)
    db.session.commit()
    
    # 204 codes don't respond with any content
    return 'Successfully deleted asset', 204

# Handles PUT and PATCH requests
def modify_asset(asset_id, new_value_dict):
    return modify_entity(Asset, asset_schema, asset_id, new_value_dict)


# ---- Team

team_schema = TeamSchema()

@events.route('/teams', methods=['POST'])
@jwt_required
def create_team():
    try:
        valid_team = team_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_team = Team(**valid_team)
    db.session.add(new_team)
    db.session.commit()
    return jsonify(team_schema.dump(new_team)), 201
    

@events.route('/teams')
@jwt_required
def read_all_teams():

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

    result = query.all()
    return jsonify(team_schema.dump(result, many=True))
    

@events.route('/teams/<team_id>')
@jwt_required
def read_one_team(team_id):
    team = db.session.query(Team).filter_by(id=team_id).first()

    if not team:
        return jsonify(f"Team with id #{team_id} does not exist."), 404

    return jsonify(team_schema.dump(team))

team_schema_no_members = TeamSchema(exclude=['members'])
person_schema = PersonSchema()
@events.route('/teams/members')
@jwt_required
def read_all_team_members():
    teams = db.session.query(Team).all()

    constructed_dict = dict()
    for team in teams:
        for member in team.members:
            member_id = member.member_id
            if member_id not in constructed_dict:
                constructed_dict[member_id] = person_schema.dump(member.member)
                constructed_dict[member_id]['active'] = member.active
                constructed_dict[member_id]['teams'] = list()
            constructed_dict[member_id]['teams'].append(team_schema_no_members.dump(team))

    return jsonify(constructed_dict)


@events.route('/teams/<team_id>', methods=['PUT'])
@jwt_required
def replace_team(team_id):
    try:
        valid_team = team_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_team(team_id, valid_team)
    

@events.route('/teams/<team_id>', methods=['PATCH'])
@jwt_required
def update_team(team_id):
    try: 
        valid_attributes = team_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_team(team_id, valid_attributes)
    

@events.route('/teams/<team_id>', methods=['DELETE'])
@jwt_required
def delete_team(team_id):
    team = db.session.query(Team).filter_by(id=team_id).first()

    if not team:
        return jsonify(f"Team with id #{team_id} does not exist."), 404
        
    setattr(team, 'active', False)
    db.session.commit()
    
    # 204 codes don't respond with any content
    return 'Successfully deleted team', 204

team_member_schema = TeamMemberSchema(exclude=['team'])

@events.route('/teams/<team_id>/members')
@jwt_required
def get_team_members(team_id):
    team_members = db.session.query(TeamMember).filter_by(team_id=team_id).all()

    if not team_members:
        return jsonify(f"Team with id #{team_id} does not have any members."), 404

    return jsonify(team_member_schema.dump(team_members, many=True))

@events.route('/teams/<team_id>/members/<member_id>', methods=['PATCH'])
@jwt_required
def modify_team_member(team_id, member_id):
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

@events.route('/teams/<team_id>/members/<member_id>', methods=['POST','PUT'])
@jwt_required
def add_team_member(team_id, member_id):
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

@events.route('/teams/<team_id>/members/<member_id>', methods=['DELETE'])
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

# Handles PUT and PATCH requests
def modify_team(team_id, new_value_dict):
    return modify_entity(Team, team_schema, team_id, new_value_dict)

# ---- Email

email_schema = EmailSchema()

@events.route('/email', methods=['POST'])
@jwt_required
def send_email():
    try:
        valid_email_request = email_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    msg = Message(valid_email_request['subject'], sender='tumissionscomputing@gmail.com', recipients=valid_email_request['recipients'])
    msg.body = valid_email_request['body']
    mail.send(msg)

    return "Sent"

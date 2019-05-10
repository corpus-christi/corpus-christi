import json
from datetime import datetime, timedelta

from flask import request, url_for, redirect
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from . import events
from .models import Event, EventPerson, EventAsset, EventParticipant, EventTeam, EventGroup, EventSchema, EventTeamSchema, EventPersonSchema, EventParticipantSchema, EventGroupSchema
from ..assets.models import Asset, AssetSchema
from ..teams.models import Team, TeamMember, TeamSchema, TeamMemberSchema
from ..emails.models import EmailSchema
from ..people.models import Person, PersonSchema
from ..images.models import Image, ImageSchema, ImageEvent, ImageEventSchema
from ..groups.models import Group, GroupSchema, Member, MemberSchema
from .. import db, mail, translate
from ..etc.helper import modify_entity, get_exclusion_list


# ---- Event

@events.route('/', methods=['POST'])
@jwt_required
def create_event():
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams', 'images', 'groups']))
    try:
        valid_event = event_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_event = Event(**valid_event)
    db.session.add(new_event)
    db.session.commit()
    return jsonify(event_schema.dump(new_event)), 201
    

@events.route('/')
def read_all_events():
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams', 'images', 'groups']))
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

    # Sorting
    sort_filter = request.args.get('sort')
    if sort_filter:
        sort_column = None
        if sort_filter[:5] == 'start':
            sort_column = Event.start
        elif sort_filter[:3] == 'end':
            sort_column = Event.end
        elif sort_filter[:5] == 'title':
            sort_column = Event.title

        if sort_filter[-4:] == 'desc' and sort_column:
            sort_column = sort_column.desc()
        
        query = query.order_by(sort_column)

    result = query.all()

    return jsonify(event_schema.dump(result, many=True))
    

@events.route('/<event_id>')
@jwt_required
def read_one_event(event_id):
    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams', 'images', 'groups']))
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

    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams', 'images', 'groups']))

    return modify_entity(Event, event_schema, event_id, valid_event)


@events.route('/<event_id>', methods=['PATCH'])
@jwt_required
def update_event(event_id):
    event_schema = EventSchema()
    try: 
        valid_attributes = event_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    event_schema = EventSchema(exclude=get_exclusion_list(request.args, ['assets', 'participants', 'persons', 'teams', 'images', 'groups']))
                
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


@events.route('/<event_id>/individuals/<person_id>', methods=['POST','PUT'])
@jwt_required
def add_event_persons(event_id, person_id):
    event_person_schema = EventPersonSchema(exclude=['event'])
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
    event_person_schema = EventPersonSchema(exclude=['event'])
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

@events.route('/<event_id>/participants/<person_id>', methods=['POST','PUT'])
@jwt_required
def add_event_participants(event_id, person_id):
    event_participant_schema = EventParticipantSchema(exclude=['event'])
    try:
        valid_confirmation = event_participant_schema.load(request.json, partial=('event_id', 'person_id'))
    except ValidationError as err:
        return jsonify(err.messages), 422

    event = db.session.query(Event).filter_by(id=event_id).first()

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
    event_participant_schema = EventParticipantSchema(exclude=['event'])
    event_person_schema = EventPersonSchema(exclude=['event'])
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

# ---- Image

@events.route('/<event_id>/images/<image_id>', methods=['POST'])
@jwt_required
def add_event_images(event_id, image_id):
    event = db.session.query(Event).filter_by(id=event_id).first()
    image = db.session.query(Image).filter_by(id=image_id).first()

    event_image = db.session.query(ImageEvent).filter_by(event_id=event_id,image_id=image_id).first()

    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    # If image is already attached to the event
    if event_image:
        return jsonify(f"Image with id #{image_id} is already attached to event with id #{event_id}."), 422
    else:
        new_entry = ImageEvent(**{'event_id': event_id, 'image_id': image_id})
        db.session.add(new_entry)
        db.session.commit()

    return jsonify(f"Image with id #{image_id} successfully added to Event with id #{event_id}."), 201

@events.route('/<event_id>/images/<image_id>', methods=['PUT'])
@jwt_required
def put_event_images(event_id, image_id):
    # check for old image id in parameter list (?old=<id>)
    old_image_id = request.args['old']
    new_image_id = image_id

    if old_image_id == 'false':
        post_resp = add_event_images(event_id, new_image_id)
        return jsonify({'deleted': 'No image to delete', 'posted': str(post_resp[0].data, "utf-8") })
    else:
        del_resp = delete_event_image(event_id, old_image_id)
        post_resp = add_event_images(event_id, new_image_id)

        if(del_resp[1] == 404):
            return jsonify({'deleted': str(del_resp[0].data, "utf-8"), 'posted': str(post_resp[0].data, "utf-8") })
        else:
            return jsonify({'deleted': del_resp[0], 'posted': str(post_resp[0].data, "utf-8") })

@events.route('/<event_id>/images/<image_id>', methods=['DELETE'])
@jwt_required
def delete_event_image(event_id, image_id):
    event_image = db.session.query(ImageEvent).filter_by(event_id=event_id,image_id=image_id).first()
    
    if not event_image:
        return jsonify(f"Image with id #{image_id} is not assigned to Event with id #{event_id}."), 404

    db.session.delete(event_image)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed image', 204


# --- Groups

@events.route('/<event_id>/groups/<group_id>', methods=['POST'])
@jwt_required
def add_event_group(event_id, group_id):
    event = db.session.query(Event).filter_by(id=event_id).first()

    group = db.session.query(Group).filter_by(id=group_id).first()

    event_group = db.session.query(EventGroup).filter_by(event_id=event_id, group_id=group_id).first()
    if not event:
        return jsonify(f"Event with id #{event_id} does not exist."), 404
    if not group:
        return jsonify(f"Group with id #{group_id} does not exist."), 404
    if not group.active:
        return jsonify(f"Group with id #{group_id} is not an active group. Activate the group before attaching it to an event."), 422
    if event_group:
        if event_group.active == True:
            return jsonify(f"Group with id #{group_id} is already attached to event with id #{event_id}."), 422
        else:
            setattr(event_group,'active', True)
    else:
        new_entry = EventGroup(**{'event_id': event_id, 'group_id': group_id, 'active': True})
        db.session.add(new_entry)

    group_members = db.session.query(Member).filter_by(group_id = group_id, active = True).all()

    for group_member in group_members:
        person_id = group_member.person_id
        if not db.session.query(EventParticipant).filter_by(event_id=event.id, person_id=person_id).first():
            new_participant = EventParticipant(**{'event_id' : event_id, 'person_id' : person_id, 'confirmed' : True})
            db.session.add(new_participant)
            # send notification
            # internationalize later
            person = db.session.query(Person).filter_by(id=person_id).first()
            person_email = person.email
            if person_email:
                print("email would be sent")
                # send_notification_email(person_email, event)

    print(translate.getTranslation('en-US','country.name.CX'))

    db.session.commit()
    return jsonify(f"Group with id #{group_id} successfully attached to event with id #{event_id}."), 201

def send_notification_email(person_email, event):
  
    # Make Python class/module that has methods like getTranslation(), getLocaleCode() 
    subj = translate.getTranslation('en-US','email.group-added-to-event.subject').gloss
    body = translate.getTranslation('en-US','email.group-added-to-event.body').gloss
    msg = Message(subj, sender='tumissionscomputing@gmail.com', recipients=[person_email])
    #link = url_for('events.read_one_event', event_id = event_id)
    ip = "http://localhost:8080"
    link = f"{ip}/event/{event.id}/details"
    print(subj,body)
    msg.html = f""+body
    mail.send(msg)

    

@events.route('/<event_id>/groups/<group_id>', methods=['DELETE'])
@jwt_required
def delete_event_group(event_id, group_id):
    event_group = db.session.query(EventGroup).filter_by(event_id=event_id, group_id=group_id).first()
    if not event_group or event_group.active == False:
        return jsonify(f"Group with id #{group_id} is not currently attached to event with id #{event_id}."), 404

    setattr(event_group,'active', False)
    db.session.commit()
    return "Image deleted from event", 204
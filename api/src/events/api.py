import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import (
    Event, EventCreate, EventUpdate, EventRead,
    EventAsset, EventTeam, EventPerson, EventPersonCreate,
    EventParticipant, EventParticipantCreate, EventGroup,
    EventSchema, EventPersonSchema, EventParticipantSchema,
)
from ..groups.models import Group, Member
from ..images.models import Image, ImageEvent
from ..people.models import Person

router = APIRouter()


# ---- Event

@router.post("/", status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_event = Event(**payload.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return EventSchema().dump(new_event)


@router.get("/")
def read_all_events(
    return_group: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = select(Event)

    if return_group == 'inactive':
        query = query.where(Event.active == False)
    elif return_group in ('all', 'both'):
        pass
    else:
        query = query.where(Event.active == True)

    if start:
        query = query.where(Event.start > (datetime.strptime(start, '%Y-%m-%d') - timedelta(days=1)))
    if end:
        query = query.where(Event.end < (datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)))
    if title:
        query = query.where(Event.title.like(f"%{title}%"))
    if location_id:
        query = query.where(Event.location_id == location_id)

    if sort:
        sort_column = None
        if sort[:5] == 'start':
            sort_column = Event.start
        elif sort[:3] == 'end':
            sort_column = Event.end
        elif sort[:5] == 'title':
            sort_column = Event.title
        if sort_column is not None:
            if sort[-4:] == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

    result = db.execute(query).scalars().all()
    return EventSchema().dump(result, many=True)


@router.get("/{event_id}")
def read_one_event(event_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    return EventSchema().dump(event)


@router.put("/{event_id}")
def replace_event(event_id: int, payload: EventCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    for key, val in payload.model_dump().items():
        setattr(event, key, val)
    db.commit()
    db.refresh(event)
    return EventSchema().dump(event)


@router.patch("/{event_id}")
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, val)
    db.commit()
    db.refresh(event)
    return EventSchema().dump(event)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    setattr(event, 'active', False)
    db.commit()


# ---- Assets

@router.post("/{event_id}/assets/{asset_id}")
def add_asset_to_event(event_id: int, asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")

    asset_events = db.execute(
        select(Event).join(EventAsset).where(EventAsset.asset_id == asset_id)
    ).scalars().all()

    for asset_event in asset_events:
        if (event.start <= asset_event.start < event.end
                or asset_event.start <= event.start < asset_event.end
                or event.start < asset_event.end <= event.end
                or asset_event.start < event.end <= asset_event.end):
            raise HTTPException(status_code=422, detail=f"Asset with id #{asset_id} is unavailable for Event with id #{event_id}.")

    new_entry = EventAsset(event_id=event_id, asset_id=asset_id)
    db.add(new_entry)
    db.commit()
    return f"Asset with id #{asset_id} successfully booked for Event with id #{event_id}."


@router.delete("/{event_id}/assets/{asset_id}", status_code=204)
def remove_asset_from_event(event_id: int, asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_asset = db.execute(
        select(EventAsset).where(EventAsset.event_id == event_id, EventAsset.asset_id == asset_id)
    ).scalar_one_or_none()
    if not event_asset:
        raise HTTPException(status_code=404, detail=f"Asset with id #{asset_id} is not booked for Event with id #{event_id}.")
    db.delete(event_asset)
    db.commit()


# ---- Teams

@router.post("/{event_id}/teams/{team_id}")
def add_event_team(event_id: int, team_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")

    event_teams = db.execute(
        select(Event).join(EventTeam).where(EventTeam.team_id == team_id)
    ).scalars().all()

    for event_team in event_teams:
        if (event.start <= event_team.start < event.end
                or event.start < event_team.end <= event.end
                or event_team.start <= event.start < event_team.end
                or event_team.start < event.end <= event_team.end):
            raise HTTPException(status_code=422, detail=f"Team with id #{team_id} is unavailable for Event with id #{event_id}.")

    new_entry = EventTeam(event_id=event_id, team_id=team_id)
    db.add(new_entry)
    db.commit()
    return f"Team with id #{team_id} successfully booked for Event with id #{event_id}."


@router.delete("/{event_id}/teams/{team_id}", status_code=204)
def delete_event_team(event_id: int, team_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_team = db.execute(
        select(EventTeam).where(EventTeam.team_id == team_id, EventTeam.event_id == event_id)
    ).scalar_one_or_none()
    if not event_team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} is not assigned to Event with id #{event_id}.")
    db.delete(event_team)
    db.commit()


# ---- Individuals (EventPerson)

@router.post("/{event_id}/individuals/{person_id}")
def add_event_persons(event_id: int, person_id: int, payload: EventPersonCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")

    event_people = db.execute(
        select(Event).join(EventPerson).where(EventPerson.person_id == person_id)
    ).scalars().all()

    for event_person in event_people:
        if (event.start <= event_person.start < event.end
                or event.start < event_person.end <= event.end
                or event_person.start <= event.start < event_person.end
                or event_person.start < event.end <= event_person.end):
            raise HTTPException(status_code=422, detail=f"Person with id #{person_id} is unavailable for Event with id #{event_id}.")

    new_entry = EventPerson(event_id=event_id, person_id=person_id, description=payload.description)
    db.add(new_entry)
    db.commit()
    return f"Person with id #{person_id} successfully booked for Event with id #{event_id}."


@router.patch("/{event_id}/individuals/{person_id}")
def modify_event_person(event_id: int, person_id: int, payload: EventPersonCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_person = db.execute(
        select(EventPerson).where(EventPerson.person_id == person_id, EventPerson.event_id == event_id)
    ).scalar_one_or_none()
    if not event_person:
        raise HTTPException(status_code=404, detail=f"Person with id #{person_id} is not associated with Event with id #{event_id}.")
    setattr(event_person, 'description', payload.description)
    db.commit()
    return EventPersonSchema().dump(event_person)


@router.delete("/{event_id}/individuals/{person_id}", status_code=204)
def delete_event_persons(event_id: int, person_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_person = db.execute(
        select(EventPerson).where(EventPerson.person_id == person_id, EventPerson.event_id == event_id)
    ).scalar_one_or_none()
    if not event_person:
        raise HTTPException(status_code=404, detail=f"Person with id #{person_id} is not assigned to Event with id #{event_id}.")
    db.delete(event_person)
    db.commit()


# ---- Participants

@router.post("/{event_id}/participants/{person_id}")
def add_event_participants(event_id: int, person_id: int, payload: EventParticipantCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")

    event_participant = db.execute(
        select(EventParticipant).where(EventParticipant.event_id == event_id, EventParticipant.person_id == person_id)
    ).scalar_one_or_none()
    if event_participant:
        raise HTTPException(status_code=422, detail=f"Person with id#{person_id} is already booked for event with id#{event_id}.")

    new_entry = EventParticipant(event_id=event_id, person_id=person_id, confirmed=payload.confirmed)
    db.add(new_entry)
    db.commit()
    return f"Person with id #{person_id} successfully booked for Event with id #{event_id}."


@router.patch("/{event_id}/participants/{person_id}")
def modify_event_participant(event_id: int, person_id: int, payload: EventParticipantCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_participant = db.execute(
        select(EventParticipant).where(EventParticipant.person_id == person_id, EventParticipant.event_id == event_id)
    ).scalar_one_or_none()
    if not event_participant:
        raise HTTPException(status_code=404, detail=f"Person with id #{person_id} is not associated with Event with id #{event_id}.")
    setattr(event_participant, 'confirmed', payload.confirmed)
    db.commit()
    return EventParticipantSchema().dump(event_participant)


@router.delete("/{event_id}/participants/{person_id}", status_code=204)
def delete_event_participant(event_id: int, person_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_participant = db.execute(
        select(EventParticipant).where(EventParticipant.person_id == person_id, EventParticipant.event_id == event_id)
    ).scalar_one_or_none()
    if not event_participant:
        raise HTTPException(status_code=404, detail=f"Person with id #{person_id} is not assigned to Event with id #{event_id}.")
    db.delete(event_participant)
    db.commit()


# ---- Images

@router.post("/{event_id}/images/{image_id}", status_code=201)
def add_event_images(event_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")
    event_image = db.execute(
        select(ImageEvent).where(ImageEvent.event_id == event_id, ImageEvent.image_id == image_id)
    ).scalar_one_or_none()
    if event_image:
        raise HTTPException(status_code=422, detail=f"Image with id #{image_id} is already attached to event with id #{event_id}.")
    new_entry = ImageEvent(event_id=event_id, image_id=image_id)
    db.add(new_entry)
    db.commit()
    return f"Image with id #{image_id} successfully added to Event with id #{event_id}."


@router.put("/{event_id}/images/{image_id}")
def put_event_images(event_id: int, image_id: int, old: Optional[str] = Query(None), db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_image_id = image_id
    if old == 'false' or old is None:
        add_event_images(event_id, new_image_id, db)
        return {'deleted': 'No image to delete', 'posted': f"Image with id #{new_image_id} successfully added to Event with id #{event_id}."}
    else:
        old_image_id = int(old)
        old_image = db.execute(
            select(ImageEvent).where(ImageEvent.event_id == event_id, ImageEvent.image_id == old_image_id)
        ).scalar_one_or_none()
        deleted_msg = 'Not found'
        if old_image:
            db.delete(old_image)
            deleted_msg = 'Successfully removed image'
        add_event_images(event_id, new_image_id, db)
        return {'deleted': deleted_msg, 'posted': f"Image with id #{new_image_id} successfully added to Event with id #{event_id}."}


@router.delete("/{event_id}/images/{image_id}", status_code=204)
def delete_event_image(event_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_image = db.execute(
        select(ImageEvent).where(ImageEvent.event_id == event_id, ImageEvent.image_id == image_id)
    ).scalar_one_or_none()
    if not event_image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} is not assigned to Event with id #{event_id}.")
    db.delete(event_image)
    db.commit()


# ---- Groups

@router.post("/{event_id}/groups/{group_id}", status_code=201)
def add_event_group(event_id: int, group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id #{event_id} does not exist.")
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group with id #{group_id} does not exist.")
    if not group.active:
        raise HTTPException(status_code=422, detail=f"Group with id #{group_id} is not an active group. Activate the group before attaching it to an event.")

    event_group = db.execute(
        select(EventGroup).where(EventGroup.event_id == event_id, EventGroup.group_id == group_id)
    ).scalar_one_or_none()

    if event_group:
        if event_group.active:
            raise HTTPException(status_code=422, detail=f"Group with id #{group_id} is already attached to event with id #{event_id}.")
        else:
            setattr(event_group, 'active', True)
    else:
        new_entry = EventGroup(event_id=event_id, group_id=group_id, active=True)
        db.add(new_entry)

    group_members = db.execute(
        select(Member).where(Member.group_id == group_id, Member.active == True)
    ).scalars().all()

    for group_member in group_members:
        pid = group_member.person_id
        existing = db.execute(
            select(EventParticipant).where(EventParticipant.event_id == event_id, EventParticipant.person_id == pid)
        ).scalar_one_or_none()
        if not existing:
            new_participant = EventParticipant(event_id=event_id, person_id=pid, confirmed=True)
            db.add(new_participant)

    db.commit()
    return f"Group with id #{group_id} successfully attached to event with id #{event_id}."


@router.delete("/{event_id}/groups/{group_id}", status_code=204)
def delete_event_group(event_id: int, group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    event_group = db.execute(
        select(EventGroup).where(EventGroup.event_id == event_id, EventGroup.group_id == group_id)
    ).scalar_one_or_none()
    if not event_group or not event_group.active:
        raise HTTPException(status_code=404, detail=f"Group with id #{group_id} is not currently attached to event with id #{event_id}.")
    setattr(event_group, 'active', False)
    db.commit()

from marshmallow import fields, Schema
from marshmallow.validate import Length, Range
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from ..db import Base
from ..shared.models import StringTypes


# ---- Event

class Event(Base):
    __tablename__ = 'events_event'
    id = Column(Integer, primary_key=True)
    title = Column(StringTypes.LONG_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    location_id = Column(Integer, ForeignKey('places_location.id'), nullable=True)
    active = Column(Boolean, default=True)
    attendance = Column(Integer)
    aggregate = Column(Boolean, default=True)

    assets = relationship("EventAsset", back_populates="event")
    teams = relationship("EventTeam", back_populates="event")
    persons = relationship("EventPerson", back_populates="event")
    participants = relationship("EventParticipant", back_populates="event")
    location = relationship("Location", back_populates="events")
    images = relationship("ImageEvent", back_populates="event")
    groups = relationship("EventGroup", back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id})>"


class EventSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    title = fields.String(required=True, validate=Length(min=1))
    description = fields.String(allow_none=True)
    start = fields.DateTime(required=True)
    end = fields.DateTime(required=True)
    location_id = fields.Integer(allow_none=True)
    active = fields.Boolean()
    attendance = fields.Integer(allow_none=True)
    aggregate = fields.Boolean(allow_none=True)

    location = fields.Nested('LocationSchema', allow_none=True, dump_only=True)
    participants = fields.Nested('EventParticipantSchema', many=True, exclude=['event'], dump_only=True)
    persons = fields.Nested('EventPersonSchema', many=True, exclude=['event'], dump_only=True)
    teams = fields.Nested('EventTeamSchema', many=True, exclude=['event'], dump_only=True)
    assets = fields.Nested('EventAssetSchema', many=True, exclude=['event'], dump_only=True)
    images = fields.Nested('ImageEventSchema', many=True, exclude=['event'], dump_only=True)
    groups = fields.Nested('EventGroupSchema', many=True, exclude=['event'], dump_only=True)


# ---- EventAsset

class EventAsset(Base):
    __tablename__ = 'events_eventasset'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    asset_id = Column(Integer, ForeignKey('events_asset.id'), primary_key=True)

    event = relationship("Event", back_populates="assets")
    asset = relationship("Asset", back_populates="events")


class EventAssetSchema(Schema):
    event = fields.Nested('EventSchema', dump_only=True)
    asset = fields.Nested('AssetSchema', dump_only=True)

    event_id = fields.Integer(required=True, min=1)
    asset_id = fields.Integer(required=True, min=1)


# ---- EventTeam

class EventTeam(Base):
    __tablename__ = 'events_eventteam'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('events_team.id'), primary_key=True)

    event = relationship("Event", back_populates="teams")
    team = relationship("Team", back_populates="events")


class EventTeamSchema(Schema):
    event_id = fields.Integer(required=True, min=1)
    team_id = fields.Integer(required=True, min=1)

    event = fields.Nested('EventSchema', dump_only=True)
    team = fields.Nested('TeamSchema', exclude=['events'], dump_only=True)


# ---- EventPerson

class EventPerson(Base):
    __tablename__ = 'events_eventperson'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)

    event = relationship("Event", back_populates="persons")
    person = relationship("Person", back_populates="events_per")


class EventPersonSchema(Schema):
    event_id = fields.Integer(required=True, min=1)
    person_id = fields.Integer(required=True, min=1)
    description = fields.String(required=True)

    event = fields.Nested('EventSchema', dump_only=True)
    person = fields.Nested('PersonSchema', dump_only=True)


# ---- EventParticipant

class EventParticipant(Base):
    __tablename__ = 'events_eventparticipant'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    confirmed = Column(Boolean, default=True)

    event = relationship("Event", back_populates="participants")
    person = relationship("Person", back_populates="events_par")


class EventParticipantSchema(Schema):
    event_id = fields.Integer(required=True, min=1)
    person_id = fields.Integer(required=True, min=1)
    confirmed = fields.Boolean()

    event = fields.Nested('EventSchema', dump_only=True)
    person = fields.Nested('PersonSchema', dump_only=True)


# ---- EventGroup

class EventGroup(Base):
    __tablename__ = 'events_eventgroup'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups_group.id'), primary_key=True)
    active = Column(Boolean, default=True)

    event = relationship("Event", back_populates="groups")
    group = relationship("Group", back_populates="events")


class EventGroupSchema(Schema):
    event_id = fields.Integer(required=True, min=1)
    group_id = fields.Integer(required=True, min=1)
    active = fields.Boolean()

    event = fields.Nested('EventSchema', dump_only=True)
    group = fields.Nested('GroupSchema', dump_only=True)

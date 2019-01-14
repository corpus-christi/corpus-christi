from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, DateTime, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..shared.models import StringTypes
from ..people.models import Person

# ---- Event

class Event(Base):
    __tablename__ = 'events_event'
    id = Column(Integer, primary_key=True)
    title = Column(StringTypes.LONG_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    location_id = Column(Integer, ForeignKey('places_location.id'), nullable=True)
    active = Column(Boolean, default=True)

    assets = relationship("EventAsset", back_populates="event")
    teams = relationship("EventTeam", back_populates="event")
    persons = relationship("EventPerson", back_populates="event")
    participants = relationship("EventParticipant", back_populates="event")
    location = relationship("Location", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id})>"
    

class EventSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    title = fields.String(required=True, validate=Length(min=1))
    description = fields.String()
    start = fields.DateTime(required=True)
    end = fields.DateTime(required=True)
    location = fields.Nested('LocationSchema', allow_null=True)
    participants = fields.Nested('EventParticipantSchema', many=True, exclude=['event'])
    persons = fields.Nested('EventPersonSchema', many=True, exclude=['event'])
    teams = fields.Nested('EventTeamSchema', many=True, exclude=['event'])
    assets = fields.Nested('EventAssetSchema', many=True, exclude=['event'])
    active = fields.Boolean()

# ---- Asset

class Asset(Base):
    __tablename__ = 'events_asset'
    id = Column(Integer, primary_key=True)
    description = Column(StringTypes.LONG_STRING)
    location_id = Column(Integer, ForeignKey('places_location.id'))
    active = Column(Boolean, default=True)

    events = relationship("EventAsset", back_populates="asset")
    location = relationship("Location", back_populates="assets")

    def __repr__(self):
        return f"<Asset(id={self.id})>"

class AssetSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    description = fields.String(required=True)
    location = fields.Nested('LocationSchema')
    active = fields.Boolean()
    event_count = fields.Integer(dump_only=True)


# ---- Team

class Team(Base):
    __tablename__ = 'events_team'
    id = Column(Integer, primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    active = Column(Boolean, default=True)
    events = relationship("EventTeam", back_populates="team")
    members = relationship("TeamMember", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id})>"
    

class TeamSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    description = fields.String(required=True)
    active = fields.Boolean()
    members = fields.Nested('TeamMemberSchema', exclude=['team'], many=True)


# ---- EventAsset

class EventAsset(Base):
    __tablename__ = 'events_eventasset'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    asset_id = Column(Integer, ForeignKey('events_asset.id'), primary_key=True)
    event = relationship("Event", back_populates="assets")
    asset = relationship("Asset", back_populates="events")

class EventAssetSchema(Schema):
    event = fields.Nested('EventSchema')
    asset = fields.Nested('AssetSchema')
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
    event = fields.Nested('EventSchema')
    team = fields.Nested('TeamSchema')
    event_id = fields.Integer(required=True, min=1)
    team_id = fields.Integer(required=True, min=1)

# ---- EventPerson

class EventPerson(Base):
    __tablename__ = 'events_eventperson'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    event = relationship("Event", back_populates="persons")
    person = relationship("Person", back_populates="events_per")

class EventPersonSchema(Schema):
    event = fields.Nested('EventSchema')
    person = fields.Nested('PersonSchema')
    description = fields.String(required=True)

# ---- TeamMember

class TeamMember(Base):
    __tablename__ = 'events_teammember'
    team_id = Column(Integer, ForeignKey('events_team.id'), primary_key=True)
    member_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    active = Column(Boolean, default=True)
    team = relationship("Team", back_populates="members")
    member = relationship("Person", back_populates="teams")

class TeamMemberSchema(Schema):
    team = fields.Nested('TeamSchema')
    member = fields.Nested('PersonSchema')
    active = fields.Boolean()

# ---- EventParticipant

class EventParticipant(Base):
    __tablename__ = 'events_eventparticipant'
    event_id = Column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    confirmed = Column(Boolean, default=True)
    event = relationship("Event", back_populates="participants")
    person = relationship("Person", back_populates="events_par")

class EventParticipantSchema(Schema):
    event = fields.Nested('EventSchema')
    person = fields.Nested('PersonSchema')
    confirmed = fields.Boolean()

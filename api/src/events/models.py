from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Event

class Event(Base):
    __tablename__ = 'events_event'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(StringTypes.LONG_STRING, nullable=True)
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('places_location.id'), nullable=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    attendance: Mapped[Optional[int]] = mapped_column(Integer)
    aggregate: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    assets = relationship("EventAsset", back_populates="event")
    teams = relationship("EventTeam", back_populates="event")
    persons = relationship("EventPerson", back_populates="event")
    participants = relationship("EventParticipant", back_populates="event")
    location = relationship("Location", back_populates="events")
    images = relationship("ImageEvent", back_populates="event")
    groups = relationship("EventGroup", back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id})>"


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    location_id: Optional[int] = None
    active: Optional[bool] = True
    attendance: Optional[int] = None
    aggregate: Optional[bool] = True


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location_id: Optional[int] = None
    active: Optional[bool] = None
    attendance: Optional[int] = None
    aggregate: Optional[bool] = None


class EventRead(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventSchema:
    """Compat shim."""
    def __init__(self, exclude=None):
        self.exclude = exclude or []

    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        result = {
            'id': obj.id,
            'title': obj.title,
            'description': obj.description,
            'start': obj.start.isoformat() if obj.start else None,
            'end': obj.end.isoformat() if obj.end else None,
            'location_id': obj.location_id,
            'active': obj.active,
            'attendance': obj.attendance,
            'aggregate': obj.aggregate,
        }
        return result

    def load(self, data, partial=False):
        return data


# ---- EventAsset

class EventAsset(Base):
    __tablename__ = 'events_eventasset'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_event.id'), primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_asset.id'), primary_key=True)

    event = relationship("Event", back_populates="assets")
    asset = relationship("Asset", back_populates="events")


# ---- EventTeam

class EventTeam(Base):
    __tablename__ = 'events_eventteam'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_event.id'), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_team.id'), primary_key=True)

    event = relationship("Event", back_populates="teams")
    team = relationship("Team", back_populates="events")


# ---- EventPerson

class EventPerson(Base):
    __tablename__ = 'events_eventperson'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)

    event = relationship("Event", back_populates="persons")
    person = relationship("Person", back_populates="events_per")


class EventPersonCreate(BaseModel):
    description: str


# ---- EventParticipant

class EventParticipant(Base):
    __tablename__ = 'events_eventparticipant'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_event.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)
    confirmed: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    event = relationship("Event", back_populates="participants")
    person = relationship("Person", back_populates="events_par")


class EventParticipantCreate(BaseModel):
    confirmed: Optional[bool] = True


class EventParticipantSchema:
    """Compat shim."""
    def __init__(self, exclude=None):
        self.exclude = exclude or []

    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'event_id': obj.event_id,
            'person_id': obj.person_id,
            'confirmed': obj.confirmed,
        }

    def load(self, data, partial=False):
        return data


class EventPersonSchema:
    """Compat shim."""
    def __init__(self, exclude=None):
        self.exclude = exclude or []

    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'event_id': obj.event_id,
            'person_id': obj.person_id,
            'description': obj.description,
        }

    def load(self, data, partial=False):
        return data


# ---- EventGroup

class EventGroup(Base):
    __tablename__ = 'events_eventgroup'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_event.id'), primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups_group.id'), primary_key=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    event = relationship("Event", back_populates="groups")
    group = relationship("Group", back_populates="events")

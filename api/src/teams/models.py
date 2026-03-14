from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Team

class Team(Base):
    __tablename__ = 'events_team'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    events = relationship("EventTeam", back_populates="team")
    members = relationship("TeamMember", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id})>"


class TeamCreate(BaseModel):
    description: str
    active: Optional[bool] = True


class TeamUpdate(BaseModel):
    description: Optional[str] = None
    active: Optional[bool] = None


class TeamRead(TeamCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TeamSchema:
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
            'id': obj.id,
            'description': obj.description,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return data


# ---- TeamMember

class TeamMember(Base):
    __tablename__ = 'events_teammember'
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('events_team.id'), primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), primary_key=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    team = relationship("Team", back_populates="members")
    member = relationship("Person", back_populates="teams")


class TeamMemberCreate(BaseModel):
    active: bool


class TeamMemberRead(TeamMemberCreate):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    member_id: int


class TeamMemberSchema:
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
            'team_id': obj.team_id,
            'member_id': obj.member_id,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return data

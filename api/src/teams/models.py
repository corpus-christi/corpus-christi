from marshmallow import fields, Schema, pre_load
from marshmallow.validate import Length, Range, OneOf
from sqlalchemy import Column, DateTime, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import Base
from ..shared.models import StringTypes

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
    members = fields.Nested('TeamMemberSchema', exclude=['team'], many=True, dump_only=True)
    events = fields.Nested('TeamMemberSchema', exclude=['member'], many=True, dump_only=True)

# ---- TeamMember

class TeamMember(Base):
    __tablename__ = 'events_teammember'
    team_id = Column(Integer, ForeignKey('events_team.id'), primary_key=True)
    member_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True)
    active = Column(Boolean, default=True)
    team = relationship("Team", back_populates="members")
    member = relationship("Person", back_populates="teams")

class TeamMemberSchema(Schema):
    team = fields.Nested('TeamSchema', dump_only=True)
    member = fields.Nested('PersonSchema', dump_only=True)
    team_id = fields.Integer(required=True, min=1)
    member_id = fields.Integer(required=True, min=1)
    active = fields.Boolean(required=True)

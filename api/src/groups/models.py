from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from src.db import Base
from src.shared.models import StringTypes


# ---- Group

class Group(Base):
    __tablename__ = 'groups_group'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    manager_id = Column(Integer, ForeignKey('people_manager.id'), nullable=False)
    manager = relationship('Manager', back_populates='groups', lazy=True)
    members = relationship('Member', back_populates='group', lazy=True)
    meetings = relationship('Meeting', back_populates='group', lazy=True)
    events = relationship('EventGroup', back_populates='group', lazy=True)
    images = relationship('ImageGroup', back_populates='group')

    def __repr__(self):
        return f"<Group(id={self.id})>"


class GroupSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    active = fields.Boolean(nullable=False)
    manager_id = fields.Integer(data_key='manager_id', required=True)
    memberList = fields.Nested('MemberSchema', many=True, only=['person','joined','active','id'])
    managerInfo = fields.Nested('ManagerSchema', only=['description_i18n','person'])


# ---- Meeting

class Meeting(Base):
    __tablename__ = 'groups_meeting'
    id = Column(Integer, primary_key=True)
    when = Column(DateTime, nullable=False)
    group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
    address_id = Column(Integer, ForeignKey('places_address.id'))
    active = Column(Boolean, nullable=False)
    group = relationship('Group', back_populates='meetings', lazy=True)
    address = relationship('Address', back_populates='meetings', lazy=True)
    members = relationship('Attendance', back_populates='meeting', lazy=True)

    def __repr__(self):
        return f"<Meeting(id={self.id})>"


class MeetingSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    when = fields.DateTime(required=True)
    group_id = fields.Integer(data_key='group_id', required=True)
    address_id = fields.Integer(data_key='address_id')
    address = fields.Nested('AddressSchema')
    active = fields.Boolean(nullable=False)
    


# ---- Member

class Member(Base):
    __tablename__ = 'groups_member'
    id = Column(Integer, primary_key=True)
    joined = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)
    group = relationship('Group', back_populates='members', lazy=True)
    person = relationship('Person', back_populates='members', lazy=True)
    meetings = relationship('Attendance', back_populates='member', lazy=True)

    def __repr__(self):
        return f"<Member(id={self.id})>"


class MemberSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    joined = fields.Date(required=True)
    active = fields.Boolean(required=True)
    group_id = fields.Integer(data_key='group_id', required=True)
    person_id = fields.Integer(data_key='person_id', required=True)
    person = fields.Nested('PersonSchema')


# ---- Attendance

class Attendance(Base):
    __tablename__ = 'groups_attendance'
    meeting_id = Column(Integer, ForeignKey('groups_meeting.id'), primary_key=True)
    member_id = Column(Integer, ForeignKey('groups_member.id'), primary_key=True)
    meeting = relationship('Meeting', back_populates='members', lazy=True)
    member = relationship('Member', back_populates='meetings', lazy=True)

    def __repr__(self):
        return f"<Attendance(meeting_id={self.meeting_id},member_id={self.member_id})>"


class AttendanceSchema(Schema):
    meeting_id = fields.Integer(data_key='meeting_id', required=True)
    member_id = fields.Integer(data_key='member_id', required=True)

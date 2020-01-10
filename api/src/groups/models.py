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
     manager_id = Column(Integer, ForeignKey(
         'people_manager.id'), nullable=False)
     meeting = relationship('Meeting', backref='groups', lazy=True)

     def __repr__(self):
            return f"<Group(id={self.id})>"


class GroupSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     name = fields.String(required=True, validate=Length(min=1))
     description = fields.String(required=True, validate=Length(min=1))
     active = fields.Boolean(required=True)
     manager_id = fields.Integer(data_key='managerId', required=True)

# ---- Meeting


class Meeting(Base):
     __tablename__ = 'groups_meeting'
     id = Column(Integer, primary_key=True)
     group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
     address_id = Column(Integer, ForeignKey('places_address.id'))
     start_time = Column(DateTime, nullable=False)
     stop_time = Column(DateTime, nullable=False)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     active = Column(Boolean, nullable=False, default=True)
     attendance = relationship('Attendance', backref='meetings', lazy=True)

     def __repr__(self):
            return f"<Meeting(id={self.id})>"


class MeetingSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     group_id = fields.Integer(data_key='groupId', required=True)
     address_id = fields.Integer(data_key='addressId')
     start_time = fields.DateTime(data_key='startTime', required=True)
     stop_time = fields.DateTime(data_key='stopTime', required=True)
     description = fields.String(required=True, validate=Length(min=1))
     active = fields.Boolean(required=True)

# ---- Member


class Member(Base):
     __tablename__ = 'groups_member'
     id = Column(Integer, primary_key=True)
     joined = Column(Date, nullable=False)
     active = Column(Boolean, nullable=False, default=True)
     group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
     person_id = Column(Integer, ForeignKey(
         'people_person.id'), nullable=False)
     group = relationship('Group', backref='members', lazy=True)
     person = relationship('Person', backref='members', lazy=True)
     attendance = relationship('Attendance', backref='members', lazy=True)

     def __repr__(self):
            return f"<Member(id={self.id})>"


class MemberSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     joined = fields.Date(required=True)
     active = fields.Boolean(required=True)
     group_id = fields.Integer(data_key='groupId', required=True)
     person_id = fields.Integer(data_key='personId', required=True)

# ---- Attendance


class Attendance(Base):
     __tablename__ = 'groups_attendance'
     meeting_id = Column(Integer, ForeignKey(
         'groups_meeting.id'), primary_key=True)
     member_id = Column(Integer, ForeignKey(
         'groups_member.id'), primary_key=True)

     def __repr__(self):
            return f"<Attendance(meeting_id={self.meeting_id},member_id={self.member_id})>"


class AttendanceSchema(Schema):
     meeting_id = fields.Integer(
         dump_only=True, data_key='meetingId', required=True)
     member_id = fields.Integer(
         dump_only=True, data_key='memberId', required=True)

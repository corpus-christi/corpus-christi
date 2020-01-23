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
    group_type_id = Column(Integer, ForeignKey(
        'groups_group_type.id'), nullable=False)
    memberships = relationship('Membership', backref='groups', lazy=True)
    managements = relationship('Management', backref='groups', lazy=True)
    meetings = relationship('Meeting', backref='group', lazy=True)
    events = relationship('EventGroup', back_populates='group', lazy=True)
    images = relationship('ImageGroup', back_populates='group', lazy=True)

    def __repr__(self):
        return f"<Group(id={self.id})>"


class GroupSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    active = fields.Boolean(required=True)
    group_type_id = fields.Integer(data_key='groupTypeId', required=True)
    memberships = fields.Nested('MembershipSchema', data_key="memberships", many=True, only=[
                                'person_id', 'joined', 'active'])
    managements = fields.Nested('ManagementSchema', data_key="managements", only=[
                                'person_id', 'management_type_id', 'active'])

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
    address = relationship('Address', back_populates='meetings', lazy=True)
    attendances = relationship('Attendance', backref='meeting', lazy=True)

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


# ---- Membership


class Membership(Base):
    __tablename__ = 'groups_membership'
    group_id = Column(Integer, ForeignKey('groups_group.id'),
                      primary_key=True, nullable=False)
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True, nullable=False)
    joined = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    group = relationship('Group', backref='members', lazy=True)
    person = relationship('Person', backref='memberships', lazy=True)

    def __repr__(self):
        return f"<Membership(group_id={self.group_id},person_id={self.person_id})>"


class MembershipSchema(Schema):
    group_id = fields.Integer(
        dump_only=True, data_key='groupId', required=True)
    person_id = fields.Integer(
        dump_only=True, data_key='personId', required=True)
    joined = fields.Date(required=True)
    active = fields.Boolean(required=True)

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

# ---- Management


class Management(Base):
    __tablename__ = 'groups_management'
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups_group.id'), primary_key=True)
    management_type_id = Column(
        Integer, ForeignKey('groups_management_type.id'))
    active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Management(group_id={self.group_id})>"


class ManagementSchema(Schema):
    person_id = fields.Integer(
        data_key='personId', required=True, validate=Range(min=1))
    group_id = fields.Integer(
        dump_only=True, data_key='groupId', required=True, validate=Range(min=1))
    management_type_id = fields.Integer(
        data_key='managementTypeId', validate=Range(min=1))
    active = fields.Boolean(required=True)

# ---- ManagementType


class ManagementType(Base):
    __tablename__ = 'groups_management_type'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    managements = relationship(
        'Management', backref='management_types', lazy=True)

    def __repr__(self):
        return f"<ManagementType(id={self.id})>"


class ManagementTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True)
    name = fields.String(required=True)

# ---- GroupType


class GroupType(Base):
    __tablename__ = 'groups_group_type'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)
    groups = relationship('Group', backref='group_types', lazy=True)

    def __repr__(self):
        return f"<GroupType(id={self.id})>"


class GroupTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True)
    name = fields.String(required=True)

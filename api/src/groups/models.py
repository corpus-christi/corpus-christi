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
    group_type_id = Column(Integer, ForeignKey(
        'groups_group_type.id'), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    members = relationship('Member', backref='group', lazy=True)
    group_type = relationship('GroupType', back_populates='groups', lazy=True)
    managers = relationship('Manager', back_populates='group', lazy=True)
    meetings = relationship('Meeting', back_populates='group', lazy=True)
    events = relationship('EventGroup', back_populates='group', lazy=True)
    images = relationship('ImageGroup', back_populates='group', lazy=True)
    member_histories = relationship(
        'MemberHistory',
        back_populates='group',
        lazy=True)

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class GroupSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    group_type_id = fields.Integer(data_key='groupTypeId', required=True)
    active = fields.Boolean(required=True)

    members = fields.Nested(
        'MemberSchema',
        dump_only=True,
        many=True,
        only=[
            'person',
            'joined',
            'active'])
    managers = fields.Nested(
        'ManagerSchema',
        dump_only=True,
        many=True,
        only=[
            'person',
            'active'])
    meetings = fields.Nested('MeetingSchema', dump_only=True, many=True,
                             only=['group_id', 'address_id', 'start_time', 'stop_time', 'description', 'active', 'attendances'])
    images = fields.Pluck('ImageGroupSchema', 'image', many=True)
    group_type = fields.Nested(
        'GroupTypeSchema',
        dump_only=True,
        data_key='groupType',
        only=[
            'id',
            'name'])
    member_histories = fields.Nested('MemberHistorySchema', many=True, dump_only=True, data_key='memberHistories',
                                     only=('id', 'joined', 'left', 'person_id'))

# ---- Group Type


class GroupType(Base):
    __tablename__ = 'groups_group_type'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)

    groups = relationship('Group', back_populates='group_type', lazy=True)

    def __repr__(self):
        return f"<GroupType(id={self.id})>"


class GroupTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))

    groups = fields.Nested(
        'GroupSchema',
        dump_only=True,
        many=True,
        only=[
            'id',
            'name',
            'active'])


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
    group = relationship('Group', back_populates='meetings', lazy=True)
    attendances = relationship(
        'Attendance',
        back_populates='meeting',
        lazy=True)

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

    address = fields.Nested('AddressSchema', dump_only=True)
    group = fields.Nested('GroupSchema', dump_only=True)
    attendances = fields.Nested(
        'AttendanceSchema',
        many=True,
        dump_only=True,
        only=['person'])


# ---- Member

class Member(Base):
    __tablename__ = 'groups_member'
    group_id = Column(
        Integer,
        ForeignKey('groups_group.id'),
        primary_key=True,
        nullable=False)
    person_id = Column(
        Integer,
        ForeignKey('people_person.id'),
        primary_key=True,
        nullable=False)
    joined = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    person = relationship('Person', back_populates='members', lazy=True)

    def __repr__(self):
        return f"<Member(person_id={self.person_id}, group_id={self.group_id})>"


class MemberSchema(Schema):
    group_id = fields.Integer(data_key='groupId', required=True)
    person_id = fields.Integer(data_key='personId', required=True)
    joined = fields.Date(required=True)
    active = fields.Boolean(required=True)
    person = fields.Nested('PersonSchema', dump_only=True)


class MemberHistory(Base):
    __tablename__ = 'groups_member_history'
    id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)
    joined = Column(Date, nullable=False)
    left = Column(Date, nullable=False)
    person = relationship(
        'Person',
        back_populates='member_histories',
        lazy=True)
    group = relationship('Group', back_populates='member_histories', lazy=True)

    def __repr__(self):
        return f"<MemberHistory(id={self.id}, "\
            f"person_id={self.person_id}, group_id={self.group_id}, "\
            f"joined={self.joined}, left={self.left})>"


class MemberHistorySchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    group_id = fields.Integer(data_key='groupId', required=True)
    person_id = fields.Integer(data_key='personId', required=True)
    joined = fields.Date(required=True)
    left = fields.Date(required=True)
    person = fields.Nested('PersonSchema', dump_only=True)
    group = fields.Nested('GroupSchema', dump_only=True)

# ---- Manager


class Manager(Base):
    __tablename__ = 'groups_manager'
    person_id = Column(
        Integer,
        ForeignKey('people_person.id'),
        primary_key=True,
        nullable=False)
    group_id = Column(
        Integer,
        ForeignKey('groups_group.id'),
        primary_key=True,
        nullable=False)
    manager_type_id = Column(Integer, ForeignKey(
        'groups_manager_type.id'), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    person = relationship('Person', back_populates='managers', lazy=True)
    group = relationship('Group', back_populates='managers', lazy=True)
    manager_type = relationship(
        'ManagerType',
        back_populates='managers',
        lazy=True)

    def __repr__(self):
        return f"<Manager(person_id={self.person_id}, group_id={self.group_id})>"


class ManagerSchema(Schema):
    person_id = fields.Integer(data_key='personId', required=True)
    group_id = fields.Integer(data_key='groupId', required=True)
    manager_type_id = fields.Integer(data_key='managerTypeId', required=True)
    active = fields.Boolean(required=True)
    person = fields.Nested('PersonSchema', dump_only=True)
    group = fields.Nested('GroupSchema', dump_only=True)
    manager_type = fields.Nested(
        'ManagerTypeSchema',
        dump_only=True,
        data_key='managerType',
        only=[
            'id',
            'name'])


# ---- Manager Type

class ManagerType(Base):
    __tablename__ = 'groups_manager_type'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)

    managers = relationship(
        'Manager',
        back_populates='manager_type',
        lazy=True)

    def __repr__(self):
        return f"<ManagerType(id={self.id})>"


class ManagerTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))
    managers = fields.Nested(
        'ManagerSchema',
        dump_only=True,
        many=True,
        only=[
            'person',
            'group',
            'active'])


# ---- Attendance

class Attendance(Base):
    __tablename__ = 'groups_attendance'
    meeting_id = Column(Integer, ForeignKey(
        'groups_meeting.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey(
        'people_person.id'), primary_key=True)
    meeting = relationship('Meeting', back_populates='attendances', lazy=True)
    person = relationship('Person', backref='attendances', lazy=True)

    def __repr__(self):
        return f"<Attendance(meeting_id={self.meeting_id},person_id={self.person_id})>"


class AttendanceSchema(Schema):
    meeting_id = fields.Integer(data_key='meetingId', required=True)
    person_id = fields.Integer(data_key='personId', required=True)
    person = fields.Nested(
        'PersonSchema', dump_only=True, only=[
            'id', 'first_name', 'last_name'])
    meeting = fields.Nested('AttendanceSchema', dump_only=True)

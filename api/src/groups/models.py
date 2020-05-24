# ERD is desired. Right now the code does not represent it. It is a work in progress. 
# The code is breaking when trying to form the relationship between management and management type

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
    group_type_id = Column(Integer, ForeignKey('group_type.id'), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    groupType = relationship('GroupType', backref='group', lazy=True) #Creating a relationship between group and group types
    members = relationship('Member', backref='group', lazy=True)
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
    group_type = fields.Integer(data_key='group_type_id', required=True)
    member_list = fields.Nested('MemberSchema', data_key="memberList", many=True, only=[
                                'person', 'joined', 'active', 'id'])

# ---- Group Type

class GroupType(Base):
    __tablename__ = 'group_type'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)

    def __repr__(self):
        return f"<Type(id={self.id})>"

class GroupTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))

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


# ---- Member

class Member(Base):
    __tablename__ = 'groups_member'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups_group.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('people_person.id'), nullable=False)
    joined = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    person = relationship('Person', back_populates='member', lazy=True)
    meeting = relationship('Attendance', backref='member', lazy=True)
    # group = relationship('Group', backref='member', lazy=True)

    def __repr__(self):
        return f"<Member(id={self.id})>"


class MemberSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    group_id = fields.Integer(data_key='groupId', required=True)
    person_id = fields.Integer(data_key='personId', required=True)
    joined = fields.Date(required=True)
    active = fields.Boolean(required=True)
    person = fields.Nested('PersonSchema')


# ---- Attendance

class Attendance(Base):
    __tablename__ = 'groups_attendance'
    meeting_id = Column(Integer, ForeignKey('groups_meeting.id'), primary_key=True) # Creating table column for meeting_id on Attendence table
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True) # Creating table column for person_id on Attendence table

    meetings = relationship('Meeting', backref='attendance', lazy=True) # Creating relationship between attendence and meetings

    def __repr__(self):
        return f"<Attendance(meeting_id={self.meeting_id},member_id={self.member_id})>"


class AttendanceSchema(Schema):
    meeting_id = fields.Integer(data_key='meetingId', required=True)
    person = fields.Nested('PersonSchema')


# ---- Management

class Management(Base):
    __tablename__ = 'groups_management'
    person_id = Column(Integer, ForeignKey('people_person.id'), primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups_group.id'), primary_key=True, nullable=False)
    management_type_id = Column(Integer, ForeignKey('group_management_type.id'), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    person = relationship('Person', backref='management', lazy=True)
    group = relationship('Group', backref='management', lazy=True)
    managementType = relationship('ManagementType', backref='management', lazy=True)


class ManagementSchema(Schema):
    person_id = fields.Integer(data_key='personId', required=True)
    group_id = fields.Integer(data_key='groupId', required=True)
    management_type_id = fields.Integer(data_key='managementTypeId', required=True)
    active = fields.Boolean(required=True)


# ---- Management Type
class ManagementType(Base):
    __tablename__ = 'group_management_type'
    id = Column(Integer, primary_key=True)
    name = Column(StringTypes.MEDIUM_STRING, nullable=False)

    def __repr__(self):
        return f"<Type(id={self.id})>"

class ManagementTypeSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name = fields.String(required=True, validate=Length(min=1))



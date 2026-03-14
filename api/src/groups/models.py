from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..db import Base
from ..shared.models import StringTypes


# ---- Group

class Group(Base):
    __tablename__ = 'groups_group'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(StringTypes.MEDIUM_STRING, nullable=False)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    manager_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_manager.id'), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    manager = relationship('Manager', back_populates='groups', lazy=True)
    members = relationship('Member', backref='group', lazy=True)
    meetings = relationship('Meeting', backref='group', lazy=True)
    events = relationship('EventGroup', back_populates='group', lazy=True)
    images = relationship('ImageGroup', back_populates='group', lazy=True)

    def __repr__(self):
        return f"<Group(id={self.id})>"


class GroupCreate(BaseModel):
    name: str
    description: str
    active: bool = True
    managerId: int


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    managerId: Optional[int] = None


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    active: bool
    managerId: int


class GroupSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'active': obj.active,
            'managerId': obj.manager_id,
        }

    def load(self, data, partial=False):
        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'active': data.get('active', True),
            'manager_id': data.get('managerId') or data.get('manager_id'),
        }


# ---- Meeting

class Meeting(Base):
    __tablename__ = 'groups_meeting'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups_group.id'), nullable=False)
    address_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('places_address.id'))
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    stop_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(StringTypes.LONG_STRING, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    address = relationship('Address', back_populates='meetings', lazy=True)
    attendances = relationship('Attendance', backref='meeting', lazy=True)

    def __repr__(self):
        return f"<Meeting(id={self.id})>"


class MeetingCreate(BaseModel):
    groupId: int
    addressId: Optional[int] = None
    startTime: datetime
    stopTime: datetime
    description: str
    active: bool = True


class MeetingUpdate(BaseModel):
    groupId: Optional[int] = None
    addressId: Optional[int] = None
    startTime: Optional[datetime] = None
    stopTime: Optional[datetime] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class MeetingRead(MeetingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MeetingSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'groupId': obj.group_id,
            'addressId': obj.address_id,
            'startTime': obj.start_time.isoformat() if obj.start_time else None,
            'stopTime': obj.stop_time.isoformat() if obj.stop_time else None,
            'description': obj.description,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return {
            'group_id': data.get('groupId') or data.get('group_id'),
            'address_id': data.get('addressId') or data.get('address_id'),
            'start_time': data.get('startTime') or data.get('start_time'),
            'stop_time': data.get('stopTime') or data.get('stop_time'),
            'description': data.get('description'),
            'active': data.get('active', True),
        }


# ---- Member

class Member(Base):
    __tablename__ = 'groups_member'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups_group.id'), nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people_person.id'), nullable=False)
    joined: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    person = relationship('Person', back_populates='members', lazy=True)
    meetings = relationship('Attendance', backref='member', lazy=True)

    def __repr__(self):
        return f"<Member(id={self.id})>"


class MemberCreate(BaseModel):
    groupId: int
    personId: int
    joined: str
    active: bool = True


class MemberRead(MemberCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MemberSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'id': obj.id,
            'groupId': obj.group_id,
            'personId': obj.person_id,
            'joined': str(obj.joined) if obj.joined else None,
            'active': obj.active,
        }

    def load(self, data, partial=False):
        return {
            'group_id': data.get('groupId') or data.get('group_id'),
            'person_id': data.get('personId') or data.get('person_id'),
            'joined': data.get('joined'),
            'active': data.get('active', True),
        }


# ---- Attendance

class Attendance(Base):
    __tablename__ = 'groups_attendance'
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups_meeting.id'), primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups_member.id'), primary_key=True)

    def __repr__(self):
        return f"<Attendance(meeting_id={self.meeting_id},member_id={self.member_id})>"


class AttendanceCreate(BaseModel):
    meetingId: int
    memberId: int


class AttendanceRead(AttendanceCreate):
    model_config = ConfigDict(from_attributes=True)


class AttendanceSchema:
    """Compat shim."""
    def dump(self, obj, many=False):
        if many:
            return [self._dump_one(o) for o in obj]
        return self._dump_one(obj)

    def _dump_one(self, obj):
        if obj is None:
            return {}
        return {
            'meetingId': obj.meeting_id,
            'memberId': obj.member_id,
        }

    def load(self, data, partial=False):
        return {
            'meeting_id': data.get('meetingId') or data.get('meeting_id'),
            'member_id': data.get('memberId') or data.get('member_id'),
        }

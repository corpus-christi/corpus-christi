import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import (
    Group, GroupCreate, GroupUpdate, GroupRead, GroupSchema,
    Meeting, MeetingCreate, MeetingUpdate, MeetingSchema,
    Member, MemberCreate, MemberSchema,
    Attendance, AttendanceCreate, AttendanceSchema,
)
from ..images.models import Image, ImageGroup
from ..people.models import Role, Manager, Person

router = APIRouter()

group_schema = GroupSchema()
meeting_schema = MeetingSchema()
member_schema = MemberSchema()
attendance_schema = AttendanceSchema()


# ---- Group

@router.post("/groups", status_code=201)
def create_group(payload: dict, db: Session = Depends(get_db), _=Depends(get_current_user)):
    payload['active'] = True
    members_to_add = payload.pop('person_ids', None)

    manager = db.get(Manager, payload.get('managerId') or payload.get('manager_id'))
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    valid_group = group_schema.load(payload)
    new_group = Group(**valid_group)
    db.add(new_group)
    db.flush()

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if members_to_add:
        for member_pid in members_to_add:
            new_member = _generate_member(db, new_group.id, member_pid, today, True)
            db.add(new_member)

    group_overseer = db.execute(select(Role).where(Role.name_i18n == "role.group-overseer")).scalar_one_or_none()
    manager_account = db.execute(select(Person).where(Person.id == manager.person_id)).scalar_one_or_none()
    if manager_account and group_overseer:
        if group_overseer not in manager_account.roles:
            manager_account.roles.append(group_overseer)

    db.commit()
    db.refresh(new_group)
    return _group_dump(new_group)


@router.get("/groups")
def read_all_groups(
    return_group: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = select(Group)
    if return_group == 'inactive':
        query = query.where(Group.active == False)
    elif return_group in ('all', 'both'):
        pass
    else:
        query = query.where(Group.active == True)
    groups = db.execute(query).scalars().all()
    return group_schema.dump(groups, many=True)


@router.get("/groups/{group_id}")
def read_one_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return _group_dump(group)


@router.get("/find_group/{group_name}/{manager}")
def find_group(group_name: str, manager: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    count = db.execute(
        select(Group).where(Group.name == group_name, Group.manager_id == manager)
    ).scalars().all()
    return len(count)


@router.patch("/groups/{group_id}", status_code=201)
def update_group(group_id: int, payload: dict, db: Session = Depends(get_db), _=Depends(get_current_user)):
    update_person_ids = payload.pop('person_ids', [])

    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    new_manager_id = payload.get('managerId') or payload.get('manager_id')
    if new_manager_id and db.get(Manager, new_manager_id) is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    if new_manager_id and new_manager_id != group.manager_id:
        group_overseer = db.execute(select(Role).where(Role.name_i18n == "role.group-overseer")).scalar_one_or_none()
        if group_overseer:
            new_manager = db.get(Manager, new_manager_id)
            if new_manager:
                manager_account = db.execute(select(Person).where(Person.id == new_manager.person_id)).scalar_one_or_none()
                if manager_account and group_overseer not in manager_account.roles:
                    manager_account.roles.append(group_overseer)

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if update_person_ids:
        old_person_ids = [m.person_id for m in group.members]
        for pid in update_person_ids:
            if pid not in old_person_ids:
                new_member = _generate_member(db, group.id, pid, today, True)
                db.add(new_member)
            else:
                existing = db.execute(
                    select(Member).where(Member.person_id == pid, Member.group_id == group_id)
                ).scalar_one_or_none()
                if existing:
                    setattr(existing, 'active', True)
        for old_pid in old_person_ids:
            if old_pid not in update_person_ids:
                del_member = db.execute(
                    select(Member).where(Member.group_id == group.id, Member.person_id == old_pid)
                ).scalar_one_or_none()
                if del_member:
                    setattr(del_member, 'active', False)

    valid_group = group_schema.load(payload)
    for key, val in valid_group.items():
        setattr(group, key, val)

    db.commit()
    db.refresh(group)
    return _group_dump(group)


@router.put("/groups/activate/{group_id}")
def activate_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    setattr(group, 'active', True)
    db.commit()
    return group_schema.dump(group)


@router.put("/groups/deactivate/{group_id}")
def deactivate_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    setattr(group, 'active', False)
    db.commit()
    return group_schema.dump(group)


# ---- Meeting

@router.post("/meetings", status_code=201)
def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_meeting = Meeting(**meeting_schema.load(payload.model_dump()))
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return meeting_schema.dump(new_meeting)


@router.get("/meetings")
def read_all_meetings(db: Session = Depends(get_db)):
    result = db.execute(select(Meeting)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No meetings found")
    return meeting_schema.dump(result, many=True)


@router.get("/meetings/group/{group_id}")
def read_all_meetings_by_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Meeting).where(Meeting.group_id == group_id)).scalars().all()
    return meeting_schema.dump(result, many=True)


@router.get("/meetings/address/{address_id}")
def read_all_meetings_by_location(address_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Meeting).where(Meeting.address_id == address_id)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No meetings found")
    return meeting_schema.dump(result, many=True)


@router.get("/meetings/{meeting_id}")
def read_one_meeting(meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.get(Meeting, meeting_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting_schema.dump(result)


@router.patch("/meetings/{meeting_id}")
def update_meeting(meeting_id: int, payload: MeetingUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    for key, val in meeting_schema.load(payload.model_dump(exclude_unset=True)).items():
        setattr(meeting, key, val)
    db.commit()
    return meeting_schema.dump(meeting)


@router.delete("/meetings/delete/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    for member in meeting.attendances:
        db.delete(member)
    db.delete(meeting)
    db.commit()
    return {'msg': f'Meeting {meeting_id} deleted'}


@router.put("/meetings/activate/{meeting_id}")
def activate_meeting(meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    setattr(meeting, 'active', True)
    db.commit()
    return meeting_schema.dump(meeting)


@router.put("/meetings/deactivate/{meeting_id}")
def deactivate_meeting(meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    setattr(meeting, 'active', False)
    db.commit()
    return meeting_schema.dump(meeting)


# ---- Member

def _generate_member(db: Session, group_id: int, person_id: int, joined: str, active: bool) -> Member:
    data = {
        'group_id': group_id,
        'person_id': person_id,
        'joined': joined,
        'active': active,
    }
    return Member(**member_schema.load(data))


@router.post("/members", status_code=201)
def create_member(payload: MemberCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valid_member = member_schema.load({**payload.model_dump(), 'active': True})
    existing = db.execute(
        select(Member).where(Member.group_id == valid_member['group_id'], Member.person_id == valid_member['person_id'])
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail='member already exists')
    new_member = Member(**valid_member)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return member_schema.dump(new_member)


@router.get("/members")
def read_all_members(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Member)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No members found")
    return member_schema.dump(result, many=True)


@router.get("/members/{member_id}")
def read_one_member(member_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.get(Member, member_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No members found")
    return member_schema.dump(result)


@router.patch("/members/{member_id}")
def update_member(member_id: int, payload: MemberCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="No members found")
    valid_member = member_schema.load(payload.model_dump())
    for key, val in valid_member.items():
        setattr(member, key, val)
    db.commit()
    return member_schema.dump(member)


@router.put("/members/activate/{member_id}")
def activate_member(member_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    setattr(member, 'active', True)
    db.commit()
    return member_schema.dump(member)


@router.put("/members/deactivate/{member_id}")
def deactivate_member(member_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    setattr(member, 'active', False)
    db.commit()
    return member_schema.dump(member)


# ---- Attendance

@router.post("/attendance", status_code=201)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valid_attendance = attendance_schema.load(payload.model_dump())
    existing = db.execute(
        select(Attendance).where(
            Attendance.meeting_id == valid_attendance['meeting_id'],
            Attendance.member_id == valid_attendance['member_id']
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail='attendance already exists')
    new_attendance = Attendance(**valid_attendance)
    db.add(new_attendance)
    db.commit()
    return attendance_schema.dump(new_attendance)


@router.get("/attendance")
def read_all_attendance(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Attendance)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No attendance records found")
    return attendance_schema.dump(result, many=True)


@router.get("/attendance/meeting/{meeting_id}")
def read_attendance_by_meeting(meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Attendance).where(Attendance.meeting_id == meeting_id)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No attendance records found")
    return attendance_schema.dump(result, many=True)


@router.get("/attendance/member/{member_id}")
def read_attendance_by_member(member_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Attendance).where(Attendance.member_id == member_id)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No attendance records found")
    return attendance_schema.dump(result, many=True)


@router.delete("/attendance", status_code=204)
def delete_attendance(payload: AttendanceCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valid_attendance = attendance_schema.load(payload.model_dump())
    meeting_id = valid_attendance['meeting_id']
    member_id = valid_attendance['member_id']
    result = db.execute(
        select(Attendance).where(Attendance.meeting_id == meeting_id, Attendance.member_id == member_id)
    ).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail=f"Attendance with member_id {member_id} and meeting_id {meeting_id} doesn't exist")
    db.delete(result)
    db.commit()


# ---- Image

@router.post("/{group_id}/images/{image_id}", status_code=201)
def add_group_images(group_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group with id #{group_id} does not exist.")
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")
    group_image = db.execute(
        select(ImageGroup).where(ImageGroup.group_id == group_id, ImageGroup.image_id == image_id)
    ).scalar_one_or_none()
    if group_image:
        raise HTTPException(status_code=422, detail=f"Image with id#{image_id} is already attached to group with id#{group_id}.")
    new_entry = ImageGroup(group_id=group_id, image_id=image_id)
    db.add(new_entry)
    db.commit()
    return f"Image with id #{image_id} successfully added to Group with id #{group_id}."


@router.put("/{group_id}/images/{image_id}")
def put_group_images(group_id: int, image_id: int, old: Optional[str] = Query(None), db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_image_id = image_id
    if old == 'false' or old is None:
        add_group_images(group_id, new_image_id, db)
        return {'deleted': 'No image to delete', 'posted': f"Image with id #{new_image_id} successfully added to Group with id #{group_id}."}
    else:
        old_image_id = int(old)
        old_image = db.execute(
            select(ImageGroup).where(ImageGroup.group_id == group_id, ImageGroup.image_id == old_image_id)
        ).scalar_one_or_none()
        deleted_msg = 'Not found'
        if old_image:
            db.delete(old_image)
            deleted_msg = 'Successfully removed image'
        add_group_images(group_id, new_image_id, db)
        return {'deleted': deleted_msg, 'posted': f"Image with id #{new_image_id} successfully added to Group with id #{group_id}."}


@router.delete("/{group_id}/images/{image_id}", status_code=204)
def delete_group_image(group_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    group_image = db.execute(
        select(ImageGroup).where(ImageGroup.group_id == group_id, ImageGroup.image_id == image_id)
    ).scalar_one_or_none()
    if not group_image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} is not assigned to Group with id #{group_id}.")
    db.delete(group_image)
    db.commit()


# ---- Helpers

def _group_dump(group):
    return group_schema.dump(group)

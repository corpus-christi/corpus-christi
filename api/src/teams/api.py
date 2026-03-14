from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import Team, TeamCreate, TeamUpdate, TeamRead, TeamMember, TeamMemberCreate, TeamMemberRead, TeamSchema, TeamMemberSchema
from ..people.models import Person, PersonSchema

router = APIRouter()


# ---- Team

@router.post("/", status_code=201)
def create_team(payload: TeamCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_team = Team(**payload.model_dump())
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return TeamSchema().dump(new_team)


@router.get("/")
def read_all_teams(
    return_group: Optional[str] = Query(None),
    desc: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = select(Team)

    if return_group == 'inactive':
        query = query.where(Team.active == False)
    elif return_group in ('all', 'both'):
        pass
    else:
        query = query.where(Team.active == True)

    if desc:
        query = query.where(Team.description.like(f"%{desc}%"))

    if sort:
        sort_column = None
        if sort[:11] == 'description':
            sort_column = Team.description
        if sort_column is not None:
            if sort[-4:] == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

    result = db.execute(query).scalars().all()
    return TeamSchema().dump(result, many=True)


@router.get("/members")
def read_all_team_members(db: Session = Depends(get_db), _=Depends(get_current_user)):
    teams = db.execute(select(Team)).scalars().all()
    team_schema = TeamSchema()
    person_schema = PersonSchema()
    constructed_dict = dict()
    for team in teams:
        for member in team.members:
            member_id = member.member_id
            if member_id not in constructed_dict:
                constructed_dict[member_id] = person_schema.dump(member.member)
                constructed_dict[member_id]['active'] = member.active
                constructed_dict[member_id]['teams'] = list()
            constructed_dict[member_id]['teams'].append(team_schema.dump(team))
    return constructed_dict


@router.get("/{team_id}")
def read_one_team(team_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not exist.")
    return TeamSchema().dump(team)


@router.put("/{team_id}")
def replace_team(team_id: int, payload: TeamCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not exist.")
    for key, val in payload.model_dump().items():
        setattr(team, key, val)
    db.commit()
    db.refresh(team)
    return TeamSchema().dump(team)


@router.patch("/{team_id}")
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not exist.")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(team, key, val)
    db.commit()
    db.refresh(team)
    return TeamSchema().dump(team)


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not exist.")
    setattr(team, 'active', False)
    db.commit()


# ---- TeamMember

@router.get("/{team_id}/members")
def get_team_members(team_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team_members = db.execute(select(TeamMember).where(TeamMember.team_id == team_id)).scalars().all()
    if not team_members:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not have any members.")
    return TeamMemberSchema().dump(team_members, many=True)


@router.post("/{team_id}/members/{member_id}")
def add_team_member(team_id: int, member_id: int, payload: TeamMemberCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id #{team_id} does not exist.")
    person = db.get(Person, member_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id #{member_id} does not exist.")

    team_member = db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.member_id == member_id)
    ).scalar_one_or_none()
    if team_member:
        raise HTTPException(status_code=422, detail=f"Person with id #{member_id} is already on Team with id #{team_id}.")

    new_entry = TeamMember(team_id=team_id, member_id=member_id, active=payload.active)
    db.add(new_entry)
    db.commit()
    return 'Team member successfully added.'


@router.patch("/{team_id}/members/{member_id}")
def modify_team_member(team_id: int, member_id: int, payload: TeamMemberCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team_member = db.execute(
        select(TeamMember).where(TeamMember.member_id == member_id, TeamMember.team_id == team_id)
    ).scalar_one_or_none()
    if not team_member:
        raise HTTPException(status_code=404, detail=f"Member with id #{member_id} is not associated with Team with id #{team_id}.")
    setattr(team_member, 'active', payload.active)
    db.commit()
    return TeamMemberSchema().dump(team_member)


@router.delete("/{team_id}/members/{member_id}", status_code=204)
def delete_team_member(team_id: int, member_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    team_member = db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.member_id == member_id)
    ).scalar_one_or_none()
    if not team_member:
        raise HTTPException(status_code=404, detail=f"Member with id #{member_id} is not on Team with id #{team_id}.")
    if not team_member.active:
        raise HTTPException(status_code=422, detail=f"Member with id #{member_id} is already set as INACTIVE on Team with id #{team_id}.")
    setattr(team_member, 'active', False)
    db.commit()

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import Attribute, AttributeRead, EnumeratedValue, EnumeratedValueRead, PersonAttribute

router = APIRouter()


class AttributeCreateRequest(BaseModel):
    attribute: Dict[str, Any]
    enumeratedValues: List[Dict[str, Any]] = []


# ---- Attribute

@router.post("/attributes", response_model=AttributeRead, status_code=201)
def create_attribute(
    payload: AttributeCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    attr_data = payload.attribute
    new_attribute = Attribute(
        name_i18n=attr_data.get('nameI18n') or attr_data.get('name_i18n'),
        type_i18n=attr_data.get('typeI18n') or attr_data.get('type_i18n'),
        seq=attr_data.get('seq'),
        active=attr_data.get('active', True),
    )
    db.add(new_attribute)
    db.flush()

    for ev_data in payload.enumeratedValues:
        ev = EnumeratedValue(
            attribute_id=new_attribute.id,
            value_i18n=ev_data.get('valueI18n') or ev_data.get('value_i18n'),
            active=ev_data.get('active', True),
        )
        db.add(ev)

    db.commit()
    db.refresh(new_attribute)
    return new_attribute


@router.get("/attributes", response_model=list[AttributeRead])
def read_all_attributes(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.execute(select(Attribute).where(Attribute.active == True)).scalars().all()


@router.get("/attributes/{attribute_id}", response_model=AttributeRead)
def read_one_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Attribute, attribute_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Attribute {attribute_id} not found")
    return result


@router.patch("/attributes/{attribute_id}", response_model=AttributeRead)
def update_attribute(
    attribute_id: int,
    payload: AttributeCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    attr_data = payload.attribute
    attribute = db.get(Attribute, attribute_id)
    if attribute is None:
        raise HTTPException(status_code=404, detail=f"Attribute {attribute_id} not found")

    update_enumerated_values = [ev for ev in payload.enumeratedValues if 'id' in ev]
    new_enumerated_values = [ev for ev in payload.enumeratedValues if 'id' not in ev]

    for new_ev in new_enumerated_values:
        ev = EnumeratedValue(
            attribute_id=attribute_id,
            value_i18n=new_ev.get('valueI18n') or new_ev.get('value_i18n'),
            active=new_ev.get('active', True),
        )
        db.add(ev)

    for update_ev in update_enumerated_values:
        old_ev = db.execute(
            select(EnumeratedValue).where(
                EnumeratedValue.attribute_id == attribute_id,
                EnumeratedValue.id == update_ev['id']
            )
        ).scalar_one_or_none()
        if old_ev is not None:
            old_ev.value_i18n = update_ev.get('valueI18n') or update_ev.get('value_i18n')

    for key, val in attr_data.items():
        mapped_key = {'nameI18n': 'name_i18n', 'typeI18n': 'type_i18n'}.get(key, key)
        if hasattr(attribute, mapped_key):
            setattr(attribute, mapped_key, val)

    db.commit()
    db.refresh(attribute)
    return attribute


@router.patch("/attributes/deactivate/{attribute_id}", response_model=AttributeRead)
def deactivate_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    attribute = db.get(Attribute, attribute_id)
    if attribute is None:
        raise HTTPException(status_code=404, detail=f"Attribute {attribute_id} not found")
    attribute.active = False
    db.commit()
    db.refresh(attribute)
    return attribute


@router.patch("/attributes/activate/{attribute_id}", response_model=AttributeRead)
def activate_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    attribute = db.get(Attribute, attribute_id)
    if attribute is None:
        raise HTTPException(status_code=404, detail=f"Attribute {attribute_id} not found")
    attribute.active = True
    db.commit()
    db.refresh(attribute)
    return attribute


# ---- EnumeratedValue

@router.post("/enumerated_values", response_model=EnumeratedValueRead, status_code=201)
def create_enumerated_value(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    ev = EnumeratedValue(
        attribute_id=payload.get('attributeId') or payload.get('attribute_id'),
        value_i18n=payload.get('valueI18n') or payload.get('value_i18n'),
        active=payload.get('active', True),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/enumerated_values", response_model=list[EnumeratedValueRead])
def read_all_enumerated_values(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.execute(select(EnumeratedValue)).scalars().all()


@router.get("/enumerated_values/{enumerated_value_id}", response_model=EnumeratedValueRead)
def read_one_enumerated_value(
    enumerated_value_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(EnumeratedValue, enumerated_value_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"EnumeratedValue {enumerated_value_id} not found")
    return result


@router.patch("/enumerated_values/{enumerated_value_id}", response_model=EnumeratedValueRead)
def update_enumerated_value(
    enumerated_value_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    ev = db.get(EnumeratedValue, enumerated_value_id)
    if ev is None:
        raise HTTPException(status_code=404, detail=f"EnumeratedValue {enumerated_value_id} not found")

    if 'valueI18n' in payload:
        ev.value_i18n = payload['valueI18n']
    if 'value_i18n' in payload:
        ev.value_i18n = payload['value_i18n']
    if 'active' in payload:
        ev.active = payload['active']

    db.commit()
    db.refresh(ev)
    return ev


@router.patch("/enumerated_values/deactivate/{enumerated_value_id}", response_model=EnumeratedValueRead)
def deactivate_enumerated_value(
    enumerated_value_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    ev = db.get(EnumeratedValue, enumerated_value_id)
    if ev is None:
        raise HTTPException(status_code=404, detail=f"EnumeratedValue {enumerated_value_id} not found")
    ev.active = False
    db.commit()
    db.refresh(ev)
    return ev


@router.patch("/enumerated_values/activate/{enumerated_value_id}", response_model=EnumeratedValueRead)
def activate_enumerated_value(
    enumerated_value_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    ev = db.get(EnumeratedValue, enumerated_value_id)
    if ev is None:
        raise HTTPException(status_code=404, detail=f"EnumeratedValue {enumerated_value_id} not found")
    ev.active = True
    db.commit()
    db.refresh(ev)
    return ev

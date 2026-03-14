from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import Asset, AssetCreate, AssetUpdate, AssetRead, AssetSchema
from ..events.models import EventAsset

router = APIRouter()


# ---- Asset

@router.post("/", status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_asset = Asset(**payload.model_dump())
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return AssetSchema().dump(new_asset)


@router.get("/")
def read_all_assets(
    return_group: Optional[str] = Query(None),
    desc: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = (
        select(Asset, func.count(EventAsset.event_id).label('event_count'))
        .outerjoin(EventAsset, Asset.id == EventAsset.asset_id)
        .group_by(Asset.id)
    )

    if return_group == 'inactive':
        query = query.where(Asset.active == False)
    elif return_group in ('all', 'both'):
        pass
    else:
        query = query.where(Asset.active == True)

    if desc:
        query = query.where(Asset.description.like(f"%{desc}%"))
    if location_id:
        query = query.where(Asset.location_id == location_id)

    if sort:
        sort_column = None
        if sort[:11] == 'description':
            sort_column = Asset.description
        if sort_column is not None:
            if sort[-4:] == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

    result = db.execute(query).all()
    schema = AssetSchema()
    temp_result = []
    for item in result:
        dumped = schema.dump(item[0])
        dumped['event_count'] = item[1]
        temp_result.append(dumped)
    return temp_result


@router.get("/{asset_id}")
def read_one_asset(asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.execute(
        select(Asset, func.count(EventAsset.event_id).label('event_count'))
        .outerjoin(EventAsset, Asset.id == EventAsset.asset_id)
        .where(Asset.id == asset_id)
        .group_by(Asset.id)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Asset with id #{asset_id} does not exist.")
    result = AssetSchema().dump(row[0])
    result['event_count'] = row[1]
    return result


@router.put("/{asset_id}")
def replace_asset(asset_id: int, payload: AssetCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with id #{asset_id} does not exist.")
    for key, val in payload.model_dump().items():
        setattr(asset, key, val)
    db.commit()
    db.refresh(asset)
    return AssetSchema().dump(asset)


@router.patch("/{asset_id}")
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with id #{asset_id} does not exist.")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(asset, key, val)
    db.commit()
    db.refresh(asset)
    return AssetSchema().dump(asset)


@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with id #{asset_id} does not exist.")
    setattr(asset, 'active', False)
    db.commit()

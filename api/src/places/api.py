from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import (
    Country, CountryRead,
    Area, AreaCreate, AreaUpdate, AreaRead,
    Address, AddressCreate, AddressUpdate, AddressRead,
    Location, LocationCreate, LocationUpdate, LocationRead
)
from ..i18n.models import I18NValue, I18NKey
from ..images.models import Image, ImageLocation

router = APIRouter()


# ---- Countries

@router.get("/countries", response_model=list[CountryRead])
def read_all_countries(db: Session = Depends(get_db)):
    return db.execute(select(Country)).scalars().all()


@router.get("/countries/{country_code}")
def read_countries(
    country_code: str,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if locale is None:
        raise HTTPException(status_code=400, detail="Missing locale")

    result = db.execute(
        select(Country.code, I18NValue.gloss)
        .where(Country.code == country_code)
        .join(I18NKey, Country.name_i18n == I18NKey.id)
        .join(I18NValue, I18NKey.id == I18NValue.key_id)
        .where(I18NValue.locale_code == locale)
    ).first()
    if result is None:
        return {}
    return {"code": result[0], "name": result[1]}


# ---- Area

@router.post("/areas", response_model=AreaRead, status_code=201)
def create_area(
    payload: AreaCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    new_area = Area(**payload.model_dump())
    db.add(new_area)
    db.commit()
    db.refresh(new_area)
    return new_area


@router.get("/areas", response_model=list[AreaRead])
def read_all_areas(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.execute(select(Area)).scalars().all()


@router.get("/areas/{area_id}", response_model=AreaRead)
def read_one_area(
    area_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Area, area_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Area with id #{area_id} does not exist.")
    return result


@router.put("/areas/{area_id}", response_model=AreaRead)
def replace_area(
    area_id: int,
    payload: AreaCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Area, area_id, payload.model_dump())


@router.patch("/areas/{area_id}", response_model=AreaRead)
def update_area(
    area_id: int,
    payload: AreaUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Area, area_id, {k: v for k, v in payload.model_dump().items() if v is not None})


@router.delete("/areas/{area_id}", status_code=204)
def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    area = db.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail=f"Area with id #{area_id} does not exist.")
    db.delete(area)
    db.commit()


# ---- Address

@router.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    new_address = Address(**payload.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


@router.get("/addresses", response_model=list[AddressRead])
def read_all_addresses(
    name: Optional[str] = Query(None),
    address: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    area_id: Optional[int] = Query(None),
    country_code: Optional[str] = Query(None),
    lat_start: Optional[float] = Query(None),
    lat_end: Optional[float] = Query(None),
    lon_start: Optional[float] = Query(None),
    lon_end: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = select(Address)
    if name:
        query = query.where(Address.name.like(f"%{name}%"))
    if address:
        query = query.where(Address.address.like(f"%{address}%"))
    if city:
        query = query.where(Address.city.like(f"%{city}%"))
    if area_id is not None:
        query = query.where(Address.area_id == area_id)
    if country_code:
        query = query.where(Address.country_code.like(f"%{country_code}%"))
    if lat_start is not None:
        query = query.where(Address.latitude >= lat_start)
    if lat_end is not None:
        query = query.where(Address.latitude <= lat_end)
    if lon_start is not None:
        query = query.where(Address.longitude >= lon_start)
    if lon_end is not None:
        query = query.where(Address.longitude <= lon_end)
    return db.execute(query).scalars().all()


@router.get("/addresses/{address_id}", response_model=AddressRead)
def read_one_address(
    address_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Address, address_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Address with id #{address_id} does not exist.")
    return result


@router.put("/addresses/{address_id}", response_model=AddressRead)
def replace_address(
    address_id: int,
    payload: AddressCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Address, address_id, payload.model_dump())


@router.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(
    address_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Address, address_id, {k: v for k, v in payload.model_dump().items() if v is not None})


@router.delete("/addresses/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    address = db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with id #{address_id} does not exist.")
    db.delete(address)
    db.commit()


# ---- Location

class LocationCreateNested(LocationCreate):
    # Extra fields for nested resolution
    country_code: Optional[str] = None
    area_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    address: Optional[str] = None
    address_name: Optional[str] = None


@router.post("/locations", response_model=LocationRead, status_code=201)
def create_location(
    payload: dict,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity

    resolving_keys = ('country_code', 'area_name', 'latitude', 'longitude', 'city', 'address', 'address_name')
    payload_data = {}
    resolve_needed = False

    for key in resolving_keys:
        if key in payload:
            resolve_needed = True
            payload_data[key] = payload.pop(key)

    if resolve_needed:
        if 'country_code' not in payload_data:
            raise HTTPException(status_code=422, detail='country_code not specified in request body')
        country = db.execute(
            select(Country).where(Country.code == payload_data['country_code'])
        ).scalar_one_or_none()
        if not country:
            raise HTTPException(status_code=404, detail=f'no country code found in database matching {payload_data["country_code"]}')
        country_code = country.code

        if 'area_name' not in payload_data:
            raise HTTPException(status_code=422, detail='area_name not specified in request body')
        area = db.execute(
            select(Area).where(Area.country_code == country_code, Area.name == payload_data['area_name'])
        ).scalar_one_or_none()
        if area:
            area_id = area.id
        else:
            area = Area(name=payload_data['area_name'], country_code=country_code, active=True)
            db.add(area)
            db.flush()
            area_id = area.id

        address_name_transform = {'address_name': 'name'}
        address_keys = ('latitude', 'longitude', 'city', 'address', 'address_name')
        address_payload = {
            k if k not in address_name_transform else address_name_transform[k]: v
            for k, v in payload_data.items() if k in address_keys
        }
        address_payload['area_id'] = area_id
        address_payload['country_code'] = country_code

        existing_address = db.execute(
            select(Address).filter_by(**address_payload)
        ).scalar_one_or_none()
        if existing_address:
            address_id = existing_address.id
        else:
            if address_payload.get('name', '') == '':
                address_payload['name'] = address_payload.get('address', '')
            address_obj = Address(**address_payload, active=True)
            db.add(address_obj)
            db.flush()
            address_id = address_obj.id

        payload['address_id'] = address_id

    new_location = Location(
        description=payload.get('description'),
        address_id=payload['address_id'],
        active=payload.get('active', True)
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.get("/locations", response_model=list[LocationRead])
def read_all_locations(db: Session = Depends(get_db)):
    return db.execute(select(Location)).scalars().all()


@router.get("/locations/{location_id}", response_model=LocationRead)
def read_one_location(
    location_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Location, location_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Location with id #{location_id} does not exist.")
    return result


@router.put("/locations/{location_id}", response_model=LocationRead)
def replace_location(
    location_id: int,
    payload: LocationCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Location, location_id, payload.model_dump())


@router.patch("/locations/{location_id}", response_model=LocationRead)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    from ..shared.helpers import modify_entity
    return modify_entity(db, Location, location_id, {k: v for k, v in payload.model_dump().items() if v is not None})


@router.delete("/locations/{location_id}", status_code=204)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    location = db.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail=f"Location with id #{location_id} does not exist.")
    db.delete(location)
    db.commit()


# ---- Image

@router.post("/{location_id}/images/{image_id}", status_code=201)
def add_location_images(
    location_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    location = db.get(Location, location_id)
    image = db.get(Image, image_id)

    if not location:
        raise HTTPException(status_code=404, detail=f"Location with id #{location_id} does not exist.")
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")

    location_image = db.execute(
        select(ImageLocation).where(ImageLocation.location_id == location_id, ImageLocation.image_id == image_id)
    ).scalar_one_or_none()
    if location_image:
        raise HTTPException(status_code=422, detail=f"Image with id#{image_id} is already attached to location with id#{location_id}.")

    new_entry = ImageLocation(location_id=location_id, image_id=image_id)
    db.add(new_entry)
    db.commit()
    return f"Image with id #{image_id} successfully added to Location with id #{location_id}."


@router.put("/{location_id}/images/{image_id}")
def put_location_images(
    location_id: int,
    image_id: int,
    old: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    old_image_id = old
    new_image_id = image_id

    if old_image_id == 'false' or old_image_id is None:
        add_location_images(location_id, new_image_id, db)
        return {'deleted': 'No image to delete', 'posted': f'Image {new_image_id} added'}
    else:
        delete_location_image(location_id, int(old_image_id), db)
        add_location_images(location_id, new_image_id, db)
        return {'deleted': f'Image {old_image_id} removed', 'posted': f'Image {new_image_id} added'}


@router.delete("/{location_id}/images/{image_id}", status_code=204)
def delete_location_image(
    location_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    location_image = db.execute(
        select(ImageLocation).where(ImageLocation.location_id == location_id, ImageLocation.image_id == image_id)
    ).scalar_one_or_none()
    if not location_image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} is not assigned to Location with id #{location_id}.")
    db.delete(location_image)
    db.commit()

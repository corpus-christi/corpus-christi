from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import Person, PersonRead, PersonCreate, PersonUpdate, Role, RoleRead, Manager, ManagerCreate, ManagerRead
from ..attributes.models import Attribute, EnumeratedValue, PersonAttribute
from ..auth.blacklist_helpers import revoke_tokens_of_account
from ..courses.models import Student
from ..events.models import EventPerson, EventParticipant
from ..images.models import Image, ImagePerson
from ..teams.models import TeamMember

router = APIRouter()


# ---- Person

@router.get("/persons/fields")
def read_person_fields(db: Session = Depends(get_db)):
    response = {'person': [], 'person_attributes': []}

    person_columns = Person.__table__.columns
    attributes = db.execute(select(Attribute).where(Attribute.active == True)).scalars().all()
    enumerated_values = db.execute(select(EnumeratedValue).where(EnumeratedValue.active == True)).scalars().all()

    for c in person_columns:
        response['person'].append({c.name: str(c.type), 'required': not c.nullable})

    for a in attributes:
        attr_dict = {
            'id': a.id,
            'nameI18n': a.name_i18n,
            'typeI18n': a.type_i18n,
            'seq': a.seq,
            'active': a.active,
        }
        attr_dict[a.name_i18n] = [
            {'id': ev.id, 'attributeId': ev.attribute_id, 'valueI18n': ev.value_i18n, 'active': ev.active}
            for ev in enumerated_values if ev.attribute_id == a.id
        ]
        response['person_attributes'].append(attr_dict)

    return response


class PersonCreateRequest(BaseModel):
    person: Dict[str, Any]
    attributesInfo: List[Dict[str, Any]] = []


@router.post("/persons", response_model=PersonRead, status_code=201)
def create_person(
    payload: PersonCreateRequest,
    db: Session = Depends(get_db)
):
    person_data = payload.person
    person_data['active'] = True

    # Clean empty strings
    for key, value in list(person_data.items()):
        if value == "" or value == 0:
            person_data[key] = None

    # Map camelCase to snake_case
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'secondLastName': 'second_last_name',
        'addressId': 'address_id',
    }
    mapped_data = {}
    for k, v in person_data.items():
        mapped_key = field_map.get(k, k)
        mapped_data[mapped_key] = v

    # Handle password hashing
    if 'password' in mapped_data:
        from werkzeug.security import generate_password_hash
        mapped_data['password_hash'] = generate_password_hash(mapped_data.pop('password'))

    new_person = Person(**{k: v for k, v in mapped_data.items() if hasattr(Person, k)})

    public_user_role = db.get(Role, 1)
    if public_user_role:
        new_person.roles.append(public_user_role)
    db.add(new_person)
    db.flush()

    for person_attribute in payload.attributesInfo:
        if person_attribute.get('enumValueId') == 0:
            person_attribute['enumValueId'] = None
        pa = PersonAttribute(
            person_id=new_person.id,
            attribute_id=person_attribute.get('attributeId') or person_attribute.get('attribute_id'),
            enum_value_id=person_attribute.get('enumValueId') or person_attribute.get('enum_value_id'),
            string_value=person_attribute.get('stringValue') or person_attribute.get('string_value'),
        )
        db.add(pa)

    db.commit()
    db.refresh(new_person)
    return new_person


@router.get("/persons", response_model=list[PersonRead])
def read_all_persons(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.execute(select(Person)).scalars().all()


@router.get("/persons/username/{username}", response_model=PersonRead)
def read_one_person_by_username(
    username: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.execute(
        select(Person).where(Person.username == username)
    ).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")
    return result


@router.get("/persons/{person_id}", response_model=PersonRead)
def read_one_person(
    person_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Person, person_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")
    return result


class PersonUpdateRequest(BaseModel):
    person: Dict[str, Any]
    attributesInfo: List[Dict[str, Any]] = []


@router.put("/persons/{person_id}", response_model=PersonRead)
def update_person(
    person_id: int,
    payload: PersonUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'secondLastName': 'second_last_name',
        'addressId': 'address_id',
    }

    for new_person_attribute in payload.attributesInfo:
        attr_id = new_person_attribute.get('attributeId') or new_person_attribute.get('attribute_id')
        old_pa = db.execute(
            select(PersonAttribute).where(
                PersonAttribute.person_id == person_id,
                PersonAttribute.attribute_id == attr_id
            )
        ).scalar_one_or_none()
        if old_pa is not None:
            old_pa.string_value = new_person_attribute.get('stringValue') or new_person_attribute.get('string_value')
            old_pa.enum_value_id = new_person_attribute.get('enumValueId') or new_person_attribute.get('enum_value_id')
        else:
            pa = PersonAttribute(
                person_id=person_id,
                attribute_id=attr_id,
                enum_value_id=new_person_attribute.get('enumValueId') or new_person_attribute.get('enum_value_id'),
                string_value=new_person_attribute.get('stringValue') or new_person_attribute.get('string_value'),
            )
            db.add(pa)

    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")

    person_data = payload.person
    for k, v in person_data.items():
        mapped_key = field_map.get(k, k)
        if mapped_key != 'roles' and hasattr(person, mapped_key):
            setattr(person, mapped_key, v)

    db.commit()
    db.refresh(person)
    return person


@router.put("/persons/deactivate/{person_id}", response_model=PersonRead)
def deactivate_person(
    person_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")
    person.active = False
    db.commit()
    db.refresh(person)
    return person


@router.put("/persons/activate/{person_id}", response_model=PersonRead)
def activate_person(
    person_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person does not exist")
    person.active = True
    db.commit()
    db.refresh(person)
    return person


@router.delete("/persons/delete/{person_id}", status_code=204)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    db.execute(select(TeamMember).where(TeamMember.member_id == person_id))
    for tm in db.execute(select(TeamMember).where(TeamMember.member_id == person_id)).scalars().all():
        db.delete(tm)
    for ep in db.execute(select(EventParticipant).where(EventParticipant.person_id == person_id)).scalars().all():
        db.delete(ep)
    for ep in db.execute(select(EventPerson).where(EventPerson.person_id == person_id)).scalars().all():
        db.delete(ep)
    for s in db.execute(select(Student).where(Student.student_id == person_id)).scalars().all():
        db.delete(s)
    for pa in db.execute(select(PersonAttribute).where(PersonAttribute.person_id == person_id)).scalars().all():
        db.delete(pa)

    db.delete(person)
    db.commit()


# ---- Accounts (compat endpoints)

@router.patch("/accounts/{person_id}", response_model=PersonRead)
def update_account(
    person_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")

    roles_to_add = payload.pop('roles', None)

    for field in ('password', 'username', 'active'):
        if field in payload:
            if field == 'password':
                person.password = payload[field]
            else:
                setattr(person, field, payload[field])

    if roles_to_add is not None:
        role_objects = []
        for role_id in roles_to_add:
            role_object = db.get(Role, role_id)
            if role_object:
                role_objects.append(role_object)
        revoke_tokens_of_account(db, person.id)
        person.roles = role_objects

    db.commit()
    db.refresh(person)
    return person


@router.put("/accounts/deactivate/{account_id}", response_model=PersonRead)
def deactivate_account(
    account_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")
    person.active = False
    db.commit()
    db.refresh(person)
    return person


@router.put("/accounts/activate/{account_id}", response_model=PersonRead)
def activate_account(
    account_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person specified was NOT found")
    person.active = True
    db.commit()
    db.refresh(person)
    return person


@router.get("/accounts/{account_id}/confirm", response_model=PersonRead)
def confirm_user_account(
    account_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person to confirm was NOT found")
    person.confirmed = True
    db.commit()
    db.refresh(person)
    return person


@router.get("/role/{role_id}/persons", response_model=list[PersonRead])
def get_persons_by_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role specified was NOT found")
    return role.persons


# ---- Roles

@router.post("/role", response_model=RoleRead, status_code=201)
def create_role(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    new_role = Role(
        name_i18n=payload.get('nameI18n') or payload.get('name_i18n'),
        active=payload.get('active', True)
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/role", response_model=list[RoleRead])
def read_all_roles(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.execute(select(Role)).scalars().all()


@router.get("/role/account/{account_id}")
def get_roles_for_account(
    account_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person does not exist")
    return [r.name_i18n for r in person.roles]


@router.get("/role/{role_id}", response_model=RoleRead)
def read_one_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Role, role_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Role does not exist")
    return result


@router.patch("/role/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role does not exist")
    if 'nameI18n' in payload:
        role.name_i18n = payload['nameI18n']
    if 'name_i18n' in payload:
        role.name_i18n = payload['name_i18n']
    if 'active' in payload:
        role.active = payload['active']
    db.commit()
    db.refresh(role)
    return role


@router.put("/role/activate/{role_id}", response_model=RoleRead)
def activate_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    role.active = True
    db.commit()
    db.refresh(role)
    return role


@router.put("/role/deactivate/{role_id}", response_model=RoleRead)
def deactivate_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    role.active = False
    db.commit()
    db.refresh(role)
    return role


@router.post("/role/{account_id}&{role_id}")
def add_role_to_account(
    account_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    role_to_add = db.get(Role, role_id)
    if role_to_add is None:
        raise HTTPException(status_code=404, detail="Role not found")

    person.roles.append(role_to_add)
    db.commit()
    revoke_tokens_of_account(db, person.id)

    roles = db.execute(
        select(Role)
        .join(Person.roles)
        .where(Person.id == account_id, Role.active == True)
    ).scalars().all()
    return [r.name_i18n for r in roles]


@router.delete("/role/{account_id}&{role_id}")
def remove_role_from_account(
    account_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, account_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    role_to_remove = db.get(Role, role_id)
    if role_to_remove is None:
        raise HTTPException(status_code=404, detail="Role specified was NOT found")

    if role_to_remove not in person.roles:
        raise HTTPException(status_code=404, detail="That Person does not have that role")

    person.roles.remove(role_to_remove)
    db.commit()
    revoke_tokens_of_account(db, account_id)
    return {'id': role_to_remove.id, 'nameI18n': role_to_remove.name_i18n, 'active': role_to_remove.active}


# ---- Manager

@router.post("/manager", response_model=ManagerRead, status_code=201)
def create_manager(
    payload: ManagerCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    new_manager = Manager(**payload.model_dump())
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return new_manager


@router.get("/manager", response_model=list[ManagerRead])
def read_all_managers(
    show_unique_persons_only: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    if show_unique_persons_only == 'Y':
        return db.execute(select(Manager).distinct(Manager.person_id)).scalars().all()
    return db.execute(select(Manager)).scalars().all()


@router.get("/manager/{manager_id}", response_model=ManagerRead)
def read_one_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    result = db.get(Manager, manager_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Manager does not exist")
    return result


@router.patch("/manager/{manager_id}", response_model=ManagerRead)
def update_manager(
    manager_id: int,
    payload: ManagerCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    manager = db.get(Manager, manager_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")
    for key, val in payload.model_dump().items():
        setattr(manager, key, val)
    db.commit()
    db.refresh(manager)
    return manager


@router.delete("/manager/{manager_id}", status_code=204)
def delete_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    manager = db.get(Manager, manager_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")
    for subordinate in manager.subordinates:
        subordinate.manager_id = None
    db.delete(manager)
    db.commit()


# ---- Image

@router.post("/{person_id}/images/{image_id}", status_code=201)
def add_people_images(
    person_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person = db.get(Person, person_id)
    image = db.get(Image, image_id)

    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id #{person_id} does not exist.")
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")

    person_image = db.execute(
        select(ImagePerson).where(ImagePerson.person_id == person_id, ImagePerson.image_id == image_id)
    ).scalar_one_or_none()
    if person_image:
        raise HTTPException(status_code=422, detail=f"Image with id#{image_id} is already attached to person with id#{person_id}.")

    new_entry = ImagePerson(person_id=person_id, image_id=image_id)
    db.add(new_entry)
    db.commit()
    return f"Image with id #{image_id} successfully added to Person with id #{person_id}."


@router.put("/{person_id}/images/{image_id}")
def put_people_images(
    person_id: int,
    image_id: int,
    old: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    old_image_id = old
    new_image_id = image_id

    if old_image_id == 'false' or old_image_id is None:
        add_people_images(person_id, new_image_id, db)
        return {'deleted': 'No image to delete', 'posted': f'Image {new_image_id} added'}
    else:
        delete_person_image(person_id, int(old_image_id), db)
        add_people_images(person_id, new_image_id, db)
        return {'deleted': f'Image {old_image_id} removed', 'posted': f'Image {new_image_id} added'}


@router.delete("/{person_id}/images/{image_id}", status_code=204)
def delete_person_image(
    person_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    person_image = db.execute(
        select(ImagePerson).where(ImagePerson.person_id == person_id, ImagePerson.image_id == image_id)
    ).scalar_one_or_none()
    if not person_image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} is not assigned to Person with id #{person_id}.")
    db.delete(person_image)
    db.commit()

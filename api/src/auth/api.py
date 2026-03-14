from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..people.models import Person, Role
from .blacklist_helpers import (
    add_token_to_database, get_user_tokens,
    revoke_token, unrevoke_token)
from .dependencies import (
    create_access_token, decode_access_token,
    get_current_user, oauth2_scheme)
from .exceptions import TokenNotFound

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    jwt: str
    username: str
    firstName: str
    lastName: str


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    person = db.execute(
        select(Person).where(Person.username == payload.username)
    ).scalar_one_or_none()

    if person is None or not person.verify_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"login": ["Invalid credentials"]}
        )

    access_token = create_access_token(data={"sub": person.username})
    # Add token to database for revokability
    add_token_to_database(db, access_token, identity_claim="sub")

    return {
        "jwt": access_token,
        "username": person.username,
        "firstName": person.first_name,
        "lastName": person.last_name
    }


@router.get("/test/jwt")
def get_test_jwt(db: Session = Depends(get_db)):
    """Only available in testing mode - returns a test JWT token."""
    from config import settings
    if not settings.testing:
        raise HTTPException(status_code=404, detail="Invalid in production mode")
    access_token = create_access_token(data={"sub": "test-user"})
    return {"jwt": access_token}


@router.get("/test/login")
def login_test(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    username = payload.get("sub")
    response = {
        'token': payload,
        'timestamps': {
            'exp': datetime.fromtimestamp(payload['exp']).isoformat(),
            'nbf': datetime.fromtimestamp(payload['nbf']).isoformat(),
            'iat': datetime.fromtimestamp(payload['iat']).isoformat(),
        }
    }
    response['username'] = username

    person = db.execute(
        select(Person).where(Person.username == username)
    ).scalar_one_or_none()
    if person is None:
        response['status'] = 'failure'
        response['person'] = f"Can't fetch <Person(username='{username}')>"
    else:
        from ..people.models import PersonSchema
        person_schema = PersonSchema()
        response['person'] = person_schema.dump(person)
        response['status'] = 'success'

    return response


@router.get("/auth/token")
def get_tokens(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_tokens = get_user_tokens(db, current_user.username)
    return [token.to_dict() for token in all_tokens]


class TokenModifyRequest(BaseModel):
    revoke: bool


@router.put("/auth/token/{token_id}")
def modify_token(
    token_id: int,
    body: TokenModifyRequest,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if body.revoke:
            revoke_token(db, token_id, current_user.username)
            return {"msg": "Token revoked"}
        else:
            unrevoke_token(db, token_id, current_user.username)
            return {"msg": "Token unrevoked"}
    except TokenNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified token was not found"
        )

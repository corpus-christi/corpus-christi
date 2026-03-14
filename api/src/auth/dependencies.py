from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt as jose_jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from ..db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "type": "access",
    })
    return jose_jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token."""
    try:
        payload = jose_jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Dependency: get the current authenticated user from JWT token."""
    from ..people.models import Person
    from .blacklist_helpers import is_token_revoked

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Check if token is revoked
    if is_token_revoked(db, payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    person = db.execute(
        select(Person).where(Person.username == username)
    ).scalar_one_or_none()
    if person is None:
        raise credentials_exception
    return person


def require_role(roles: List[str]):
    """Dependency factory that checks user has at least one of the given roles."""
    def check_role(current_user=Depends(get_current_user)):
        user_role_names = [r.name_i18n for r in current_user.roles]
        for role in roles:
            if role in user_role_names:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this page, please contact your system administrator if this is a mistake."
        )
    return check_role

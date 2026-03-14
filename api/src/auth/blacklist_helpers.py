from datetime import datetime

from jose import jwt as jose_jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from .exceptions import TokenNotFound
from .models import TokenBlacklist


def _epoch_utc_to_datetime(epoch_utc):
    """Convert epoch timestamps (as stored in JWTs) into python datetime objects."""
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(db: Session, encoded_token: str, identity_claim: str = "sub"):
    """Adds a new token to the database. It is not revoked when it is added."""
    decoded_token = jose_jwt.decode(
        encoded_token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
    )
    jti = decoded_token['jti']
    token_type = decoded_token.get('type', 'access')
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.add(db_token)
    db.commit()


def is_token_revoked(db: Session, decoded_token: dict) -> bool:
    """Checks if the given token is revoked or not."""
    jti = decoded_token['jti']
    token = db.execute(
        select(TokenBlacklist).where(TokenBlacklist.jti == jti)
    ).scalar_one_or_none()
    if token is None:
        return True
    return token.revoked


def get_user_tokens(db: Session, user_identity: str):
    """Returns all tokens for the given user."""
    return db.execute(
        select(TokenBlacklist).where(TokenBlacklist.user_identity == user_identity)
    ).scalars().all()


def revoke_token(db: Session, token_id: int, user: str):
    """Revokes the given token. Raises a TokenNotFound error if not found."""
    token = db.execute(
        select(TokenBlacklist).where(
            TokenBlacklist.id == token_id,
            TokenBlacklist.user_identity == user
        )
    ).scalar_one_or_none()
    if token is None:
        raise TokenNotFound(f"Could not find the token {token_id}")
    token.revoked = True
    db.commit()


def revoke_tokens_of_account(db: Session, person_id: int):
    """Revoke all tokens belonging to an account."""
    from src.people.models import Person
    account = db.get(Person, person_id)
    if account is None:
        raise TokenNotFound("Could not find token")
    account_tokens = db.execute(
        select(TokenBlacklist).where(TokenBlacklist.user_identity == account.username)
    ).scalars().all()
    for token in account_tokens:
        token.revoked = True
    db.commit()


def unrevoke_token(db: Session, token_id: int, user: str):
    """Unrevokes the given token. Raises a TokenNotFound error if not found."""
    token = db.execute(
        select(TokenBlacklist).where(
            TokenBlacklist.id == token_id,
            TokenBlacklist.user_identity == user
        )
    ).scalar_one_or_none()
    if token is None:
        raise TokenNotFound(f"Could not find the token {token_id}")
    token.revoked = False
    db.commit()


def prune_database(db: Session):
    """Delete tokens that have expired from the database."""
    now = datetime.now()
    expired = db.execute(
        select(TokenBlacklist).where(TokenBlacklist.expires < now)
    ).scalars().all()
    for token in expired:
        db.delete(token)
    db.commit()

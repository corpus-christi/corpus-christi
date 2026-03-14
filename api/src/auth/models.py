from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class TokenBlacklist(Base):
    __tablename__ = 'auth_blacklist'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False)
    token_type: Mapped[str] = mapped_column(String(10), nullable=False)
    user_identity: Mapped[str] = mapped_column(String(50), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    expires: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }

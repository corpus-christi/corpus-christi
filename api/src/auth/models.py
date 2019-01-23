import os
import json

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime

from ..db import Base
from .. import db

class TokenBlacklist(Base):
    __tablename__ = 'auth_blacklist'
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    token_type = Column(String(10), nullable=False)
    user_identity = Column(String(50), nullable=False)
    revoked = Column(Boolean, nullable=False)
    expires = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }
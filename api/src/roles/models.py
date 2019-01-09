from marshmallow import Schema, fields
from marshmallow.validate import Range
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from src.db import Base
from src.shared.models import StringTypes


# ---- Role


people_account_role = Table('people_account_role', Base.metadata,
                            Column('account_id', Integer,
                                   ForeignKey('people_account.id')),
                            Column('role_id', Integer,
                                   ForeignKey('people_role.id'))
                            )


class Role(Base):
    __tablename__ = 'people_role'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.LOCALE_CODE)
    active = Column(Boolean)
    accounts = relationship(
        "Account",
        secondary=people_account_role,
        back_populates="roles", lazy=True)

    def __repr__(self):
        return f"<Role(id={self.id})>"


class RoleSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    active = fields.Boolean()

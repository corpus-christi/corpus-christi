from marshmallow import Schema, fields
from marshmallow.validate import Range
from sqlalchemy import Column, Integer

from src.db import Base
from src.shared.models import StringTypes


# ---- Role


class Role(Base):
    __tablename__ = 'roles_role'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.LOCALE_CODE)

    def __repr__(self):
        return f"<Role(id={self.id},name='{self.name_i18n}')>"


class RoleSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')

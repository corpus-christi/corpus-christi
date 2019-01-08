from marshmallow import Schema, fields
from marshmallow.validate import Range
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from src.db import Base
from src.shared.models import StringTypes


# ---- Role
people_account_role = Table('people_account_role', Base.metadata,
             Column('account_id', Integer, ForeignKey('people_account.id')),
             Column('role_id', Integer, ForeignKey('people_role.id'))
    )

class Role(Base):
    __tablename__ = 'people_role'
    id = Column(Integer, primary_key=True)
    name_i18n = Column(StringTypes.LOCALE_CODE)
    active = Column(Boolean)
    account = relationship(
        "Account",
        secondary=people_account_role,
        backref="people_role", lazy = True)


    def __repr__(self):
        return f"<Role(id={self.id})>"


class RoleSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    name_i18n = fields.String(data_key='nameI18n')
    active = fields.Boolean()
#
# # ---- Account Role
#
# class Account_Role(Base):
#     __tablename__ = 'people_account_role'
#     account_id = Column(Integer, ForeignKey('people_account.id'), primary_key=True)
#     role_id = Column(Integer, ForeignKey('people_role.id'), primary_key=True)
#
#
#     def __repr__(self):
#         return f"<Account Role(account_id={self.account_id},role_id={self.role_id})>"
#
#
# class Account_RoleSchema(Schema):
#     account_id = fields.Integer(dump_only=True, data_key='accountId', required=True, validate=Range(min=1))
#     role_id = fields.Integer(dump_only=True, data_key='roleId', required=True, validate=Range(min=1))
#

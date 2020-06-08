from marshmallow import Schema, fields
from marshmallow.validate import Range, Length
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from src.db import Base
from src.shared.models import StringTypes

# ---- Error-report

class ErrorReport(Base):
    __tablename__ = 'error_report'
    id = Column(Integer, primary_key=True)
    description = Column(StringTypes.LONG_STRING, nullable=False)
    time_stamp = Column(DateTime, nullable=False)
    status_code = Column(Integer)
    endpoint = Column(StringTypes.MEDIUM_STRING, nullable=False)
    solved = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Error-report(id={self.id})>"


class ErrorReportSchema(Schema):
    id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
    description = fields.String(required=True, validate=Length(min=1))
    time_stamp = fields.DateTime(required=True)
    status_code = fields.Integer(allow_none=True)
    endpoint = fields.String(required=True, validate=Length(min=1))
    solved = fields.Boolean()

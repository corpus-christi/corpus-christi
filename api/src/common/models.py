from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    phone_number = db.Column(db.Text)
    gender = db.Column(db.Text)
    birthday = db.Column(db.Text)
    password = db.Column(db.Text)
    baptism_status = db.Column(db.Boolean)
    marital_status_id = db.Column(db.Integer, ForeignKey('marital_status.id'))
    how_did_you_find_out_id = db.Column(db.Integer, ForeignKey('how_did_you_find_out.id'))
    is_a_parent = db.Column(db.Boolean)
    join_date = db.Column(db.Text)
    deactivation_date = db.Column(db.Text)
    attributes = db.Column(db.JSON)

    attendances = relationship("Attendance")
    homegroup_roles = relationship("HomegroupPersonRole")

"""
Configure courses Blueprint
"""
from flask import Blueprint
from . import api

courses = Blueprint('courses', __name__)

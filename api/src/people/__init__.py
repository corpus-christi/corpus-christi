from flask import Blueprint

people = Blueprint('people', __name__)

from . import api

from flask import Blueprint

places = Blueprint('places', __name__)

from . import api

from flask import Blueprint

attributes = Blueprint('attributes', __name__)

from . import api

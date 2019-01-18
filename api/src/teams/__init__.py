from flask import Blueprint

teams = Blueprint('teams', __name__)

from . import api

from flask import Blueprint

events = Blueprint('events', __name__)

from . import api

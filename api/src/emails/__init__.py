from flask import Blueprint

emails = Blueprint('emails', __name__)

from . import api

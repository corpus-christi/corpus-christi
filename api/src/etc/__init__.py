from flask import Blueprint

etc = Blueprint('etc', __name__)

from . import api

from flask import Blueprint

gather = Blueprint('groups', __name__)

from . import views

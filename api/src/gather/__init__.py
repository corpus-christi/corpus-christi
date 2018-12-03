from flask import Blueprint

gather = Blueprint('gather', __name__)

from . import views

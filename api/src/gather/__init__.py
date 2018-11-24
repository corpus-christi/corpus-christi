from flask import Blueprint

gather = Blueprint('gather', __name__,
                   template_folder='templates',
                   static_folder='static')

from . import views

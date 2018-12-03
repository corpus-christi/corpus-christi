from flask import Blueprint

common = Blueprint('common', __name__)

from . import i18n

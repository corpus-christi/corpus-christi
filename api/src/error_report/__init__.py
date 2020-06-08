from flask import Blueprint

error_report = Blueprint('error_report', __name__)

from . import api

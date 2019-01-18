import json
from datetime import datetime, timedelta

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from . import images
from .. import db, mail
from ..etc.helper import modify_entity, get_exclusion_list

import os
from datetime import datetime

from flask import jsonify
from src.auth.utils import jwt_not_required

from . import etc


@etc.route('/ping')
@jwt_not_required
def ping():
    """Basic smoke test that application server is running."""
    return jsonify({
        'ping': 'pong',
        'os': os.name,
        'cwd': os.getcwd(),
        'pid': os.getpid(),
        'now': datetime.now(),
        'utc': datetime.utcnow()
    })

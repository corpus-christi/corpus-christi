import os
from datetime import datetime

from flask import jsonify

from . import etc


@etc.route('/ping')
def ping():
    """Basic smoke test that application server is running."""
    return jsonify({
        'ping': 'pong',
        'os': os.name,
        'cwd': os.getcwd(),
        'pid': os.getpid(),
        'uid': os.getuid(),
        'now': datetime.now(),
        'utc': datetime.utcnow()
    })

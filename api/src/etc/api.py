import os
from datetime import datetime

from flask import jsonify

from ..auth.utils import jwt_not_required
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
"""
@courses.route('/courses/<course_id>', methods=['PUT'])
@jwt_not_required
def replace_course(course_id):
    pass

@courses.route('/courses/<course_id>', methods=['DELETE'])
@jwt_not_required
def delete_course(course_id):
    pass

@courses.route('/prerequisites/<prerequisite_id>')
@jwt_not_required
def read_one_prerequisite(prerequisite_id):
    result = db.session.query(Prerequisite).filter_by(id=prerequisite_id).first()
    return jsonify(prerequisite_schema.dump(result))


@courses.route('/prerequisites/<prerequisite_id>', methods=['PUT'])
@jwt_not_required
def replace_prerequisite(prerequisite_id):
    pass

@courses.route('/prerequisites/<prerequisite_id>', methods=['DELETE'])
@jwt_not_required
def delete_prerequisite(prerequisite_id):
    pass

@courses.route('/course_offerings/<course_offering_id>', methods=['PUT'])
@jwt_not_required
def replace_course_offering(course_offering_id):
    pass

@courses.route('/course_offerings/<course_offering_id>', methods=['DELETE'])
@jwt_not_required
def delete_course_offering(course_offering_id):
    pass
    """

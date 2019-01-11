import json

from flask import request
from flask.json import jsonify, dumps
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
import sys

from . import courses
from .models import Course, CourseSchema, Course_Offering, Course_OfferingSchema, PrerequisiteSchema
from .. import db

course_schema = CourseSchema()


@courses.route('/courses', methods=['POST'])
@jwt_required
def create_course():
    """Create an active (by default) course"""
    try:
        valid_course = course_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_course = Course(**valid_course)
    db.session.add(new_course)
    db.session.commit()
    return jsonify(course_schema.dump(new_course)), 201


@courses.route('/courses')
@jwt_required
def read_all_courses():
    """List all active and inactive courses"""
    result = db.session.query(Course).all()
    results = course_schema.dump(result, many=True) # Courses are now JSON

    # Runs through range of list values to access both lists at read_one_course
    # (SQLAlchemy object and python dictionary)
    for i in range(0, len(results)): # iterate through json results
        results[i]['prerequisites'] = []
        for j in result[i].prerequisites: # get list of prerequisites
            j = course_schema.dump(j, many=False)
            results[i]['prerequisites'].append(j)
    return jsonify(results)


@courses.route('/courses-active')
@jwt_required
def read_all_active_courses():
    """List all active courses"""
    result = db.session.query(Course).filter_by(active=True).all()
    return jsonify(course_schema.dump(result, many=True))


@courses.route('/courses-inactive')
@jwt_required
def read_all_inactive_courses():
    """List all inactive courses"""
    result = db.session.query(Course).filter_by(active=False).all()
    return jsonify(course_schema.dump(result, many=True))


@courses.route('/courses/<course_id>')
@jwt_required
def read_one_course(course_id):
    """List only one course with given course_id"""
    result = db.session.query(Course).filter_by(id=course_id).first()
    return jsonify(course_schema.dump(result))


@courses.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required
def update_course(course_id):
    """Update course with given course_id with appropriate details"""

    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Not Found', 404
    for attr in "description", "active", "name":
        if attr in request.json:
            setattr(course, attr, request.json[attr])
    db.session.commit()
    return jsonify(course_schema.dump(course))


@courses.route('/courses/deactivate/<course_id>', methods=['PATCH'])
@jwt_required
def deactivate_course(course_id):
    """Set active course with given course_id to inactive (False)"""
    valid_course = db.session.query(Course).filter_by(id=course_id).first()
    if valid_course is None:
        return 'Not Found', 404
    else:
        setattr(valid_course, 'active', False)
    db.session.commit()
    return jsonify(course_schema.dump(valid_course))


@courses.route('/courses/reactivate/<course_id>', methods=['PATCH'])
@jwt_required
def reactivate_course(course_id):
    """Set inactive course with given course_id to active (True)"""
    valid_course = db.session.query(Course).filter_by(id=course_id).first()
    if valid_course is None:
        return 'Not Found', 404
    else:
        setattr(valid_course, 'active', True)
    db.session.commit()
    return jsonify(course_schema.dump(valid_course))


# ---- Prerequisite

prerequisite_schema = PrerequisiteSchema()

"""
Route adds prerequisite for a specific course
"""
@courses.route('/courses/prerequisites/<course_id>', methods=['POST'])
@jwt_required
def create_prerequisite(course_id):
    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Course not found', 404
    course.prerequisites.append(db.session.query(Course).filter_by(id=request.json['prereq_id']).first())
    db.session.commit()
    return jsonify(course_schema.dump(course)), 201

"""
Route reads all prerequisites in database
--Might not need later
"""
@courses.route('/courses/prerequisites')
@jwt_required
def read_all_prerequisites():
    result = db.session.query(Course).all() #Get courses to get prereq's
    results = [] # new list
    for i in result:
        for j in i.prerequisite: # Read through course prerequisites
            results.append(j)
    return jsonify(course_schema.dump(results, many=True))

# read all courses with prereq (?)


@courses.route('/courses/prerequisites/<course_id>')
def read_one_course_prerequisites(course_id):
    result = db.session.query(Course).filter_by(id=course_id).first()
    prereqs_to_return = []
    for i in result.prerequisite:
        prereqs_to_return.append(i)
    return jsonify(course_schema.dump(prereqs_to_return, many=True))



@courses.route('/courses/prerequisites/<prerequisite_id>', methods=['PATCH'])
@jwt_required
def update_prerequisite(prerequisite_id):
    try:
        valid_prerequisite = prerequisite_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    prerequisite = db.session.query(
        Prerequisite).filter_by(id=prerequisite_id).first()

    for key, val in valid_prerequisite.items():
        setattr(prerequisite, key, val)

    db.session.commit()
    return jsonify(prerequisite_schema.dump(prerequisite))


# ---- Course_Offering

course_offering_schema = Course_OfferingSchema()


@courses.route('/course_offerings', methods=['POST'])
@jwt_required
def create_course_offering():
    try:
        valid_course_offering = course_offering_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_course_offering = Course_Offering(**valid_course_offering)
    db.session.add(new_course_offering)
    db.session.commit()
    return jsonify(course_offering_schema.dump(new_course_offering)), 201


@courses.route('/course_offerings')
@jwt_required
def read_all_course_offerings():
    result = db.session.query(Course_Offering).all()
    return jsonify(course_offering_schema.dump(result, many=True))

# read all active course offerings
# read all inactive course offerings


@courses.route('/course_offerings/<course_offering_id>')
@jwt_required
def read_one_course_offering(course_offering_id):
    result = db.session.query(Course_Offering).filter_by(
        id=course_offering_id).first()
    return jsonify(course_offering_schema.dump(result))


@courses.route('/course_offerings/<course_offering_id>', methods=['PATCH'])
@jwt_required
def update_course_offering(course_offering_id):
    # try:
    #     valid_course_offering = course_offering_schema.load(request.json)
    # except ValidationError as err:
    #     return jsonify(err.messages), 422

    course_offering = db.session.query(
        Course_Offering).filter_by(id=course_offering_id).first()
    if course_offering is None:
        return "Course Offering NOT Found", 404

    for attr in 'description', "active", "max_size":
        if attr in request.json:
            setattr(course_offering, attr, request.json[attr])

    db.session.commit()
    return jsonify(course_offering_schema.dump(course_offering))

#Completed by Ryan and Eliza 01/08/2019 2:45pm

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import courses
from .models import Course, CourseSchema, Course_Offering, Course_OfferingSchema, PrerequisiteSchema #Prerequisite
from .. import db

course_schema = CourseSchema()

@courses.route('/courses', methods=['POST'])
@jwt_required
def create_course():
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
    result = db.session.query(Course).all()
    return jsonify(course_schema.dump(result, many=True))

@courses.route('/courses-active')
@jwt_required
def read_all_active_courses():
    result = db.session.query(Course).filter_by(active=True).all()
    return jsonify(course_schema.dump(result, many=True))

@courses.route('/courses-inactive')
@jwt_required
def read_all_inactive_courses():
    result = db.session.query(Course).filter_by(active=False).all()
    return jsonify(course_schemadump(result, many=True))

@courses.route('/courses/<course_id>')
@jwt_required
def read_one_course(course_id):
    print('You found the page for course id %d. Congrats' % course_id)
    result = db.session.query(Course).filter_by(id=course_id).first()
    return jsonify(course_schema.dump(result))


@courses.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required
def update_course(course_id):
    try:
        valid_course = course_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course = db.session.query(Course).filter_by(id=course_id).first()

    for key, val in valid_course.items():
        setattr(course, key, val)

    db.session.commit()
    return jsonify(course_schema.dump(course))

# deactivate course
@courses.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required
def deactivate_course(course_id):
    try:
        valid_course = course_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course = db.session.query(Course).filter_by(id=course_id).first()

    if 'active' in request.json: #valid_course:
        setattr(course, 'active', False)

    db.session.commit()
    return jsonify(course_schema.dump(course))

# reactivate course
@courses.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required
def reactivate_course(course_id):
    try:
        valid_course = course_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course = db.session.query(Course).filter_by(id=course_id).first()

    if "active" in request.json:
        setattr(course, 'active', True)


# ---- Prerequisite

prerequisite_schema = PrerequisiteSchema()

@courses.route('/prerequisites', methods=['POST'])
@jwt_required
def create_prerequisite():
    try:
        valid_prerequisite = prerequisite_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_prerequisite = Prerequisite(**valid_prerequisite)
    db.session.add(new_prerequisite)
    db.session.commit()
    return jsonify(prerequisite_schema.dump(new_prerequisite)), 201


@courses.route('/prerequisites')
@jwt_required
def read_all_prerequisites():
    result = db.session.query(Prerequisite).all()
    return jsonify(prerequisite_schema.dump(result, many=True))

# read all courses with prereq (?)

@courses.route('/prerequisites/<prerequisite_id>', methods=['PATCH'])
@jwt_required
def update_prerequisite(prerequisite_id):
    try:
        valid_prerequisite = prerequisite_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    prerequisite = db.session.query(Prerequisite).filter_by(id=prerequisite_id).first()

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
    result = db.session.query(Course_Offering).filter_by(id=course_offering_id).first()
    return jsonify(course_offering_schema.dump(result))


@courses.route('/course_offerings/<course_offering_id>', methods=['PATCH'])
@jwt_required
def update_course_offering(course_offering_id):
    try:
        valid_course_offering = course_offering_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course_offering = db.session.query(Course_Offering).filter_by(id=course_offering_id).first()

    for key, val in valid_course_offering.items():
        setattr(course_offering, key, val)

    db.session.commit()
    return jsonify(course_offering_schema.dump(course_offering))

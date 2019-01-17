import json

from flask import request
#from flask_api import status
from flask.json import jsonify, dumps
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from ..shared.utils import authorize
import sys
from datetime import datetime

from . import courses
from ..people.models import Person, PersonSchema
from .models import Course, CourseSchema, \
    Course_Offering, Course_OfferingSchema, \
    Student, StudentSchema, Class_Attendance, \
    Class_AttendanceSchema, Class_Meeting, \
    Class_MeetingSchema
from src.people.models import Person
from .. import db

course_schema = CourseSchema()


@courses.route('/courses', methods=['POST'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
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


"""
Function that takes a SQLAlchemy query of Courses and
adds its prerequisites, returning as a jsonified object
"""


def add_prereqs(query_result):
    if(hasattr(query_result, '__iter__')):
        courses = course_schema.dump(query_result, many=True)
        for i in range(0, len(courses)):
            courses[i]['prerequisites'] = []
            for j in query_result[i].prerequisites:
                j = course_schema.dump(j, many=False)
                courses[i]['prerequisites'].append(j)
    else:
        courses = course_schema.dump(query_result, many=False)
        courses['prerequisites'] = []
        for i in query_result.prerequisites:
            i = course_schema.dump(i, many=False)
            courses['prerequisites'].append(i)
    return courses


"""
Helper function applies course offerings to course
inputted by the user
"""


def include_course_offerings(course):
    course['course_offerings'] = []
    offerings = db.session.query(Course_Offering).filter_by(
        course_id=course['id']).all()
    for i in offerings:
        course['course_offerings'].append(course_offering_schema.dump(i))
    return course


@courses.route('/courses')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public", ])
def read_all_courses():
    """List all active and inactive courses"""
    result = db.session.query(Course).all()
    if(result == []):
        return "Result NOT found", 404
    with_prereqs = add_prereqs(result)
    for i in with_prereqs:
        include_course_offerings(i)
    return jsonify(with_prereqs)


@courses.route('/<active_state>/courses')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_active_state_of_courses(active_state):
    """List all active courses"""
    result = db.session.query(Course)
    if(active_state == 'active'):
        result = result.filter_by(active=True).all()
    elif(active_state == 'inactive'):
        result = result.filter_by(active=False).all()
    else:
        return "Result NOT found", 404
    # return jsonify(add_prereqs(result))
    return jsonify(course_schema.dump(result, many=True))


@courses.route('/courses/<course_id>')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_one_course(course_id):
    """List only one course with given course_id"""
    result = db.session.query(Course).filter_by(id=course_id).first()
    if result is None:
        return "Result NOT found", 404
    with_prereqs = add_prereqs(result)
    with_offerings = include_course_offerings(with_prereqs)
    return jsonify(with_offerings)


@courses.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
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


# ---- Prerequisite
"""
Route adds prerequisite for a specific course
"""


@courses.route('/courses/<course_id>/prerequisites', methods=['POST'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def create_prerequisite(course_id):
    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Course to add prereqs not found', 404
    for p in request.json['prerequisites']:
        if(p == course.id):
            continue  # don't add course as it's own prerequisite
        course.prerequisites.append(
            db.session.query(Course).filter_by(id=p).first())
    db.session.commit()
    return jsonify(course_schema.dump(course)), 201


"""
Route reads all prerequisites in database
--Might not need later
"""


@courses.route('/courses/prerequisites')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_all_prerequisites():
    result = db.session.query(Course).all()  # Get courses to get prereq's
    if result == []:
        return 'No courses found', 404
    results = []  # new list
    for i in result:
        for j in i.prerequisites:  # Read through course prerequisites
            results.append(j)
    return jsonify(course_schema.dump(results, many=True))


@courses.route('/courses/<course_id>/prerequisites')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_one_course_prerequisites(course_id):
    result = db.session.query(Course).filter_by(id=course_id).first()
    if result is None:
        return 'Course not found', 404
    prereqs_to_return = []
    for i in result.prerequisites:
        prereqs_to_return.append(i)
    return jsonify(course_schema.dump(prereqs_to_return, many=True))


@courses.route('/courses/prerequisites/<course_id>', methods=['PATCH'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def update_prerequisite(course_id):
    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Course to update prereqs not found', 404
    for i in course.prerequisites:
        if not (i.id in request.json['prerequisites']):
            course.prerequisites.remove(i)
    for i in request.json['prerequisites']:
        if(i == course.id):
            continue  # don't add course as it's own prerequisite
        course.prerequisites.append(
            db.session.query(Course).filter_by(id=i).first())
    db.session.commit()
    return jsonify(course_schema.dump(course))


# ---- Course_Offering

course_offering_schema = Course_OfferingSchema()


@courses.route('/course_offerings', methods=['POST'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
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
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_all_course_offerings():
    result = db.session.query(Course_Offering).all()
    if result == []:
        return 'No Course Offerings found', 404
    results = course_offering_schema.dump(result, many=True)
    for r in results:
        r['course'] = course_schema.dump(db.session.query(
            Course).filter_by(id=r['courseId']).first(), many=False)
    return jsonify(results)


@courses.route('/course_offerings/<course_offering_id>')
@jwt_required
# @authorize(["role.superuser", "role.public"])
def read_one_course_offering(course_offering_id):
    result = course_offering_schema.dump(db.session.query(Course_Offering).filter_by(id=course_offering_id).first())
    result['course'] = course_schema.dump(db.session.query(Course).filter_by(id=result['courseId']).first())
    return jsonify(result)


@courses.route('/<active_state>/course_offerings')
@jwt_required
def read_active_state_course_offerings(active_state):
    result = db.session.query(Course_Offering)
    if (active_state == 'active'):
        query = result.filter_by(active=True).all()
    elif (active_state == 'inactive'):
        query = result.filter_by(active=False).all()
    else:
        return 'Cannot filter course offerings with undefined state', 404
    return jsonify(course_offering_schema.dump(query, many=True))


@courses.route('/course_offerings/<course_offering_id>', methods=['PATCH'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def update_course_offering(course_offering_id):
    course_offering = db.session.query(
        Course_Offering).filter_by(id=course_offering_id).first()
    if course_offering is None:
        return "Course Offering NOT Found", 404

    for attr in 'description', 'active', 'max_size':
        if attr in request.json:
            setattr(course_offering, attr, request.json[attr])

    db.session.commit()
    return jsonify(course_offering_schema.dump(course_offering))

# ---- Student


student_schema = StudentSchema()


@courses.route('/course_offerings/<s_id>', methods=['POST'])
@jwt_required
def add_student_to_course_offering(s_id):
    try:
        valid_student = student_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course_offering = request.json['offeringId']
    courseInDB = db.session.query(Student).filter_by(
        student_id=s_id, offering_id=course_offering).all()
    if courseInDB == []:
        new_student = Student(**valid_student)

        db.session.add(new_student)
        db.session.commit()
        return jsonify(student_schema.dump(new_student)), 201
    else:
        return 'Student already enrolled in course offering', 208


@courses.route('/course_offerings/<course_offering_id>/students')
@jwt_required
def read_all_course_offering_students(course_offering_id):
    """ This function lists all students by a specific course offering.
        Students are listed regardless of confirmed or active state. """
    stu_result = db.session.query(Student).filter_by(
        offering_id=course_offering_id).all()
    co_result = db.session.query(Course_Offering).filter_by(
        id=course_offering_id).first()

    if stu_result is [] or co_result is None:
        return 'The specified course offering does not exist \
                or there are no students enrolled in the course offering ', 404

    # Serialize specific course offering into json obj
    offering = course_offering_schema.dump(co_result, many=False)
    # Create new students dictionary into a specific course offering
    offering['students'] = []
    # Serialize every student from query result into json obj
    s = student_schema.dump(stu_result, many=True)
    # Add json object of all student objects into the course offering
    offering['students'].append(s)
    return jsonify(offering)


# May not need this route unless UI says so...
# @courses.route('/students')
# @jwt_required
# def read_all_students():
#     result = db.session.query(Student).all()
#     return jsonify(student_schema.dump(result, many=True))


@courses.route('/students/<student_id>')
@jwt_required
def read_one_student(student_id):
    result = db.session.query(Student).filter_by(id=student_id).first()
    if result is None:
        return 'Student not found', 404
    return jsonify(student_schema.dump(result))


@courses.route('/students/<student_id>', methods=['PATCH'])
@jwt_required
def update_student(student_id):
    student = db.session.query(Student).filter_by(id=student_id).first()
    if student is None:
        return "Student not found", 404

    for attr in 'confirmed', 'active':
        if attr in request.json:
            setattr(student, attr, request.json[attr])

    db.session.commit()
    return jsonify(student_schema.dump(student))


# ---- Class_Meeting

class_meeting_schema = Class_MeetingSchema()

@courses.route('/course_offerings/<int:course_offering_id>/class_meetings', methods=['POST'])
@jwt_required
def create_class_meeting(course_offering_id):
    """ Create and add class meeting into course offering. """
    try:
        valid_class_meeting = class_meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    meetingInDB = db.session.query(Class_Meeting).filter_by(
        offering_id=course_offering_id,
        teacher_id=request.json['teacherId'],
        when=datetime.strptime(request.json['when'], '%Y-%m-%d %H:%M:%S') ).first() # Todo: make sure when is datetime obj

    # If a class meeting for a course offering DNE
    if meetingInDB is None:
        # Create and add new class meeting to course offering
        new_class_meeting = Class_Meeting(**valid_class_meeting)
        db.session.add(new_class_meeting)
        db.session.commit()
        return jsonify(class_meeting_schema.dump(new_class_meeting)), 201
    else:
        # If a class meeting has entry with same offering, teacher, and datetime
        # then don't create new class meeting
        return 'Class meeting already exists in course offering', 208


@courses.route('/course_offerings/<int:course_offering_id>/class_meetings')
@jwt_required
def read_all_class_meetings(course_offering_id):
    result = db.session.query(Class_Meeting).filter_by(offering_id=course_offering_id).all()
    if result == []:
        return 'No class meetings found for this course offering', 404
    return jsonify(class_meeting_schema.dump(result, many=True))


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>')
@jwt_required
def read_one_class_meeting(course_offering_id, class_meeting_id):
    result = db.session.query(Class_Meeting).filter_by(id=class_meeting_id, offering_id=course_offering_id).first()
    if result is None:
        return 'Specified class meeting does not exist for this course offering', 404
    return jsonify(class_meeting_schema.dump(result))


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>', methods=['PATCH'])
@jwt_required
def update_class_meeting(course_offering_id, class_meeting_id):
    class_meeting = db.session.query(Class_Meeting).filter_by(id=class_meeting_id, offering_id=course_offering_id).first()
    if class_meeting is None:
           return "Class meeting not found", 404 

    for attr in 'location_id', 'teacher_id', 'when':
        if attr in request.json:
            if attr == 'when':
                # For example, the following line requires datetime input to be "2019-02-01 10:01:30"
                request.json['when'] = datetime.strptime(request.json['when'], '%Y-%m-%d %H:%M:%S')
            setattr(class_meeting, attr, request.json[attr])

    db.session.commit()
    return jsonify(class_meeting_schema.dump(class_meeting))

@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>', methods=['DELETE'])
@jwt_required
def delete_class_meeting(course_offering_id, class_meeting_id):
    class_meeting = db.session.query(Class_Meeting).filter_by(id=class_meeting_id, offering_id=course_offering_id).first()
    class_attended = db.session.query(Class_Attendance).filter_by(class_id=class_meeting_id).first()

    # If class meeting exists with no class attendance, then delete meeting
    if class_meeting is not None and class_attended is None:
        db.session.delete(class_meeting)
        db.session.commit()
        return 'Class meeting successfully deleted', 200
    # If class meeting DNE
    elif class_meeting is None:
        return 'Course offering does not exist', 404
    else:
        return 'Students have attended the class meeting. Cannot delete class meeting.', 403


# ---- Class_Attendance

class_attendance_schema = Class_AttendanceSchema()

"""
Helper function applies attendance with student name to
a class meeting
**NOTE**: The meeting must be a Class_MeetingSchema dumped object
"""
def add_attendance_to_meetings(json_meeting):
    json_meeting['attendance'] = []
    attendance = db.session.query(Class_Attendance, Student, Person).filter_by(class_id=json_meeting['id']).join(Student).join(Person).all()
    for i in attendance:
        json_meeting['attendance'].append({ "classId" : i.class_id, "studentId" : i.student_id, "name" : i.Person.full_name() })
    return json_meeting


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>/class_attendance', methods=['POST'])
@jwt_required
def add_class_attendance(course_offering_id, class_meeting_id):
    """ Create new entries of attendance """
    # assume a list of (valid) student id's // EX: [1, 2, 3, 4]
    class_meeting = db.session.query(Class_Meeting).filter_by(id=class_meeting_id).first()
    new_attendance = []
    for i in request.json['attendance']:
        student = db.session.query(Student).filter_by(id=i, offering_id=course_offering_id).first()
        if student is None:
            continue # Student isn't enrolled in course offering or doesn't exist
        student.attendance.append(class_meeting)
        new_attendance.append(student)
    db.session.add_all(new_attendance)
    db.session.commit()
    return jsonify(add_attendance_to_meetings(class_meeting_schema.dump(class_meeting)))


@courses.route('/course_offerings/<course_offering_id>/class_attendance')
@jwt_required
def read_one_class_attendance(course_offering_id):
    """ Get all attendance from a single course """
    meetings = class_meeting_schema.dump(db.session.query(Class_Meeting).filter_by(offering_id=course_offering_id).all(), many=True)
    if meetings == []:
        return 'Class Meetings NOT found for this course offering', 404
    for i in meetings:
        add_attendance_to_meetings(i)
    return jsonify(meetings)


@courses.route('/course_offerings/<course_offering_id>/<class_meeting_id>/class_attendance')
@jwt_required
def read_one_meeting_attendance(course_offering_id, class_meeting_id):
    """ Get attendance for a single class """
    meeting = class_meeting_schema.dump(db.session.query(Class_Meeting).filter_by(offering_id=course_offering_id, id=class_meeting_id).first())
    if meeting is None:
        return 'Class Meeting NOT found', 404
    add_attendance_to_meetings(meeting)
    return jsonify(meeting)


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>/class_attendance', methods=['PATCH'])
@jwt_required
def update_class_attendance(course_offering_id, class_meeting_id):
    # assume a list of valid student id's // EX: [1, 2, 4]
    current_attendance = class_attendance_schema.dump(db.session.query(Class_Attendance).filter_by(class_id=class_meeting_id).all(), many=True)
    class_meeting = db.session.query(Class_Meeting).filter_by(id=class_meeting_id).first()
    updated_attendance = []
    for i in request.json['attendance']:
        updated_attendance.append({"classId" : class_meeting_id, "studentId" : i})
    updates = []
    #Delete missing
    for i in current_attendance:
        if i not in updated_attendance:
            student = db.session.query(Student).filter_by(id=i['studentId'], offering_id=course_offering_id).first()
            if student is None:
                continue # Student isn't enrolled in course offering or doesn't exist
            student.attendance.remove(class_meeting)
            updates.append(student)

    #Now to add new things
    for i in updated_attendance:
        if i not in current_attendance:
            student = db.session.query(Student).filter_by(id=i['studentId'], offering_id=course_offering_id).first()
            if student is None:
                continue # Student isn't enrolled in course offering or doesn't exist
            student.attendance.append(class_meeting)
            updates.append(student)

    db.session.add_all(updates)
    db.session.commit() # Commit all new changes
    return jsonify(add_attendance_to_meetings(class_meeting_schema.dump(class_meeting)))


# ---- Class_Meeting
person_schema = PersonSchema()
class_meeting_schema = Class_MeetingSchema()

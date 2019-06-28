from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from . import courses
from .models import Course, CourseSchema, \
    Course_Offering, Student, StudentSchema, \
    Diploma, DiplomaSchema, CourseOfferingSchema, \
    DiplomaCourse, DiplomaAwarded, DiplomaAwardedSchema, \
    ClassAttendance, ClassAttendanceSchema, \
    ClassMeetingSchema, \
    CourseCompletion, CourseCompletionSchema
from .. import db
from ..images.models import Image, ImageCourse
from ..people.models import Person, PersonSchema
from ..places.models import LocationSchema

# OBJECT SCHEMA
class_attendance_schema = ClassAttendanceSchema()
class_meeting_schema = ClassMeetingSchema()
course_completion_schema = CourseCompletionSchema()
course_offering_schema = CourseOfferingSchema()
course_schema = CourseSchema()
diploma_awarded_schema = DiplomaAwardedSchema()
diploma_schema = DiplomaSchema()
location_schema = LocationSchema()
person_schema = PersonSchema()
student_schema = StudentSchema()


# -- Courses


def add_prereqs(query_result):
    """ Helper function that takes a SQLAlchemy query of Courses and
        adds its prerequisites, returning as a jsonified object. """
    if (hasattr(query_result, '__iter__')):
        courses = course_schema.dump(query_result, many=True)
        for i in range(0, len(courses)):
            courses[i]['prerequisites'] = []
            for j in query_result[i].prerequisites:
                j = course_schema.dump(j, many=False)
                del j['diplomaList']
                courses[i]['prerequisites'].append(j)
    else:
        courses = course_schema.dump(query_result, many=False)
        courses['prerequisites'] = []
        for i in query_result.prerequisites:
            i = course_schema.dump(i, many=False)
            courses['prerequisites'].append(i)
    return courses


def include_course_offerings(course):
    """ Helper function applies course offerings to course inputted by the user. """
    course['course_offerings'] = []
    offerings = db.session.query(Course_Offering).filter_by(
        course_id=course['id']).all()
    for i in offerings:
        course['course_offerings'].append(course_offering_schema.dump(i))
    return course


@courses.route('/courses', methods=['POST'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def create_course():
    """ Create an active (by default) course. """
    if 'active' not in request.json:
        request.json['active'] = True
    try:
        valid_course = course_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_course = Course(**valid_course)
    db.session.add(new_course)
    db.session.commit()
    return jsonify(course_schema.dump(new_course)), 201


@courses.route('/courses')
# @authorize(["role.superuser", "role.registrar", "role.public", ])
def read_all_courses():
    """ List all active and inactive courses. """
    result = db.session.query(Course).all()
    if (result == []):
        return "Result NOT found", 404
    for course in result:
        course.diplomaList = course.diplomas
    with_prereqs = add_prereqs(result)
    for i in with_prereqs:
        include_course_offerings(i)
    return jsonify(with_prereqs)


@courses.route('/<string:active_state>/courses')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_active_state_of_courses(active_state):
    """ List all courses with given active state. """
    result = db.session.query(Course)
    if (active_state == 'active'):
        result = result.filter_by(active=True).all()
    elif (active_state == 'inactive'):
        result = result.filter_by(active=False).all()
    else:
        return "Result NOT found", 404
    return jsonify(course_schema.dump(result, many=True))


@courses.route('/courses/<int:course_id>')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_one_course(course_id):
    """ List only one course with given course_id. """
    result = db.session.query(Course).filter_by(id=course_id).first()
    if result is None:
        return "Result NOT found", 404
    with_prereqs = add_prereqs(result)
    with_offerings = include_course_offerings(with_prereqs)
    return jsonify(with_offerings)


@courses.route('/courses/<int:course_id>', methods=['PATCH'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def update_course(course_id):
    """ Update course with given course_id with appropriate details. """
    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Not Found', 404

    try:
        valid_course = course_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    for attr in "description", "active", "name":
        if attr in request.json:
            setattr(course, attr, request.json[attr])
    db.session.commit()
    return jsonify(course_schema.dump(course))


# ---- Prerequisite


@courses.route('/courses/<int:course_id>/prerequisites', methods=['POST'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def create_prerequisite(course_id):
    """ Route adds prerequisite for a specific course. """
    course = db.session.query(Course).filter_by(id=course_id).first()
    if course is None:
        return 'Course to add prereqs not found', 404
    for p in request.json['prerequisites']:
        if (p == course.id):
            continue  # don't add course as it's own prerequisite
        course.prerequisites.append(
            db.session.query(Course).filter_by(id=p).first())
    db.session.commit()
    return jsonify(course_schema.dump(course)), 201


@courses.route('/courses/prerequisites')
@jwt_required
# @authorize(["role.superuser", "role.registrar", "role.public"])
def read_all_prerequisites():
    """ Route reads all prerequisites in database. """
    result = db.session.query(Course).all()  # Get courses to get prereq's
    if result == []:
        return 'No courses found', 404
    results = []  # new list
    for i in result:
        for j in i.prerequisites:  # Read through course prerequisites
            results.append(j)
    return jsonify(course_schema.dump(results, many=True))


@courses.route('/courses/<int:course_id>/prerequisites')
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


@courses.route('/courses/<int:course_id>/prerequisites', methods=['PATCH'])
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
        if (i == course.id):
            continue  # don't add course as it's own prerequisite
        course.prerequisites.append(
            db.session.query(Course).filter_by(id=i).first())
    db.session.commit()
    return jsonify(course_schema.dump(course))


# ---- Course_Offering

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


@courses.route('/course_offerings/<int:course_offering_id>')
@jwt_required
# @authorize(["role.superuser", "role.public"])
def read_one_course_offering(course_offering_id):
    result = course_offering_schema.dump(db.session.query(
        Course_Offering).filter_by(id=course_offering_id).first())
    result['course'] = course_schema.dump(db.session.query(
        Course).filter_by(id=result['courseId']).first())
    return jsonify(result)


@courses.route('/<string:active_state>/course_offerings')
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


@courses.route('/course_offerings/<int:course_offering_id>', methods=['PATCH'])
@jwt_required
# @authorize(["role.superuser", "role.registrar"])
def update_course_offering(course_offering_id):
    course_offering = db.session.query(
        Course_Offering).filter_by(id=course_offering_id).first()
    if course_offering is None:
        return "Course Offering NOT Found", 404

    course_offering_json = course_offering_schema.load(
        request.json, partial=True)
    for attr in course_offering_json.keys():
        setattr(course_offering, attr, course_offering_json[attr])

    db.session.commit()
    return jsonify(course_offering_schema.dump(course_offering))


# ---- Diploma

@courses.route('/diplomas', methods=['POST'])
@jwt_required
def create_diploma():
    courseList = []
    if 'courseList' in request.json:
        courseList = request.json['courseList']
        del request.json['courseList']
    try:
        valid_diploma = diploma_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_diploma = Diploma(**valid_diploma)
    for course_id in courseList:
        course = db.session.query(Course).filter_by(id=course_id).first()
        new_diploma.courses.append(course)

    db.session.add(new_diploma)
    db.session.commit()
    new_diploma.courseList = new_diploma.courses
    return jsonify(diploma_schema.dump(new_diploma)), 201


@courses.route('/diplomas')
@jwt_required
def read_all_diplomas():
    """ Read all diplomas in database """
    result = db.session.query(Diploma).all()
    if result == []:
        return 'No Diplomas found', 404
    for diploma in result:
        diploma.courseList = diploma.courses
        students = []
        for da in diploma.diplomas_awarded:
            students.append(da.students)
        diploma.studentList = students
    return jsonify(diploma_schema.dump(result, many=True))


@courses.route('/diplomas/<int:diploma_id>')
@jwt_required
def read_one_diploma(diploma_id):
    """ Read info for one diploma """
    result = db.session.query(Diploma).filter_by(id=diploma_id).first()
    if result is None:
        return jsonify(msg="Diploma not found"), 404

    result.courseList = result.courses
    students = []
    for da in result.diplomas_awarded:
        students.append(da.students)
    result.studentList = students
    return jsonify(diploma_schema.dump(result))


@courses.route('/diplomas/<int:diploma_id>', methods=['PATCH'])
@jwt_required
def update_diploma(diploma_id):
    """ Update one diploma """
    diploma = db.session.query(Diploma).filter_by(id=diploma_id).first()
    if diploma is None:
        return jsonify(f'Diploma with id #{diploma_id} not found'), 404

    courseList = []
    if 'courseList' in request.json:
        courseList = request.json['courseList']
        del request.json['courseList']

    try:
        valid_diploma = diploma_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    for key, val in valid_diploma.items():
        setattr(diploma, key, val)

    if courseList:
        diploma.courses = []
        for course_id in courseList:
            course = db.session.query(Course).filter_by(id=course_id).first()
            diploma.courses.append(course)

    db.session.commit()
    diploma.courseList = diploma.courses
    return jsonify(diploma_schema.dump(diploma))


@courses.route('/diplomas/<int:diploma_id>/<int:course_id>', methods=['PUT'])
@jwt_required
def add_course_to_diploma(diploma_id, course_id):
    """ Append course to diploma """
    diploma = db.session.query(Diploma).filter_by(id=diploma_id).first()
    course = db.session.query(Course).filter_by(id=course_id).first()

    if course not in diploma.courses:
        diploma.courses.append(course)
    else:
        return jsonify(msg='Course already in diploma'), 409
    db.session.commit()
    diploma.courseList = diploma.courses
    return jsonify(diploma_schema.dump(diploma))


@courses.route('/diplomas/<int:diploma_id>/<int:course_id>', methods=['DELETE'])
@jwt_required
def remove_course_from_diploma(diploma_id, course_id):
    """ Remove course from diploma """
    diploma = db.session.query(Diploma).filter_by(id=diploma_id).first()
    course = db.session.query(Course).filter_by(id=course_id).first()

    # If diploma is associated with course
    if course in diploma.courses:
        # And if no diplomas have been awarded
        if diploma.diplomas_awarded == []:
            # Delete association between diploma and course
            diploma.courses.remove(course)
        else:
            return jsonify(f'Student was awarded diploma #{diploma.id}'), 403
    else:
        return jsonify(f'Course #{course.id} not associated with diploma #{diploma.id}'), 404
    db.session.commit()
    diploma.courseList = diploma.courses
    return 'Successfully deleted course association with diploma', 200


@courses.route('/diplomas/activate/<int:diploma_id>', methods=['PATCH'])
@jwt_required
def activate_diploma(diploma_id):
    """ Set diploma's `active` attribue to TRUE """
    diploma = db.session.query(Diploma).filter_by(id=diploma_id).first()
    if diploma is None:
        return 'Not Found', 404
    setattr(diploma, 'active', True)
    db.session.commit()

    return jsonify(diploma_schema.dump(diploma))


@courses.route('/diplomas/deactivate/<int:diploma_id>', methods=['PATCH'])
@jwt_required
def deactivate_diploma(diploma_id):
    """ Set diploma's `active` attribue to False """
    diploma = db.session.query(Diploma).filter_by(id=diploma_id).first()
    if diploma is None:
        return 'Not Found', 404
    setattr(diploma, 'active', False)
    db.session.commit()

    return jsonify(diploma_schema.dump(diploma))


# ---- DiplomaAwarded


@courses.route('/diplomas_awarded', methods=['POST'])
@jwt_required
def create_diploma_awarded():
    try:
        print(request.json)
        valid_diploma_awarded = diploma_awarded_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_diploma_awarded = DiplomaAwarded(**valid_diploma_awarded)
    check = db.session.query(DiplomaAwarded).filter_by(person_id=new_diploma_awarded.person_id,
                                                       diploma_id=new_diploma_awarded.diploma_id).first()
    if check:
        return jsonify(
            msg=f'Diploma #{new_diploma_awarded.diploma_id} already awarded to person #{new_diploma_awarded.person_id}'), 409

    db.session.add(new_diploma_awarded)
    db.session.commit()
    return jsonify(diploma_awarded_schema.dump(new_diploma_awarded)), 201


@courses.route('/diplomas_awarded')
@jwt_required
def read_all_diplomas_awarded():
    result = db.session.query(DiplomaAwarded).all()
    if result == []:
        return 'No Diplomas Awarded found', 404
    # Currently does not show student objects for each student.. may want to show
    return jsonify(diploma_awarded_schema.dump(result, many=True))


# MIGHT NOT NEED? // Needs diploma_id and Person.person_id to get a desirable query result
@courses.route('/diplomas_awarded/<int:person_id>/<int:diploma_id>')
@jwt_required
def read_one_diploma_awarded(person_id, diploma_id):
    """ Get details of the diploma awarded. """
    result = db.session.query(DiplomaAwarded).filter_by(
        person_id=person_id, diploma_id=diploma_id).first()
    if result is None:
        return jsonify(f'Diploma for person #{person_id} and diploma #{diploma_id} not found'), 404
    return jsonify(diploma_awarded_schema.dump(result))


@courses.route('/diplomas_awarded/<int:diploma_id>/students')
@jwt_required
def read_all_students_diploma_awarded(diploma_id):
    """ Read all students that were awarded with the diploma id. """
    result = db.session.query(Diploma, DiplomaAwarded, Person).filter_by(
        id=diploma_id).join(DiplomaAwarded, Person).all()
    if result == []:
        return jsonify(f'No results for diploma with id #{diploma_id} found'), 404
    diploma = diploma_schema.dump(result[0].Diploma)
    diploma['students'] = []
    for i in result:
        p = person_schema.dump(i.Person)
        p['diplomaAwarded'] = diploma_awarded_schema.dump(i.DiplomaAwarded)[
            'when']
        diploma['students'].append(p)
    return jsonify(diploma)


@courses.route('/diplomas_awarded/<int:diploma_id>/<int:person_id>', methods=['PATCH'])
@jwt_required
def update_diploma_awarded(diploma_id, person_id):
    """ Update `when` attribute of diploma """
    diploma_awarded = db.session.query(DiplomaAwarded) \
        .filter_by(diploma_id=diploma_id, person_id=person_id).first()
    if diploma_awarded is None:
        return jsonify(f'Diploma with id {diploma_id} not found'), 404

    try:
        valid_diploma_awarded = diploma_awarded_schema.load(
            request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    if 'when' in request.json:
        setattr(diploma_awarded, 'when', valid_diploma_awarded['when'])

    db.session.commit()
    return jsonify(diploma_awarded_schema.dump(diploma_awarded))


@courses.route('/diplomas_awarded/<int:diploma_id>/<int:person_id>', methods=['DELETE'])
@jwt_required
def delete_diploma_awarded(diploma_id, person_id):
    """ Remove a student's diploma """
    diploma_awarded = db.session.query(DiplomaAwarded) \
        .filter_by(diploma_id=diploma_id, person_id=person_id).first()
    if diploma_awarded is None:
        return jsonify(msg=f"That diploma #{diploma_id} for student #{person_id} does not exist"), 404
    db.session.delete(diploma_awarded)
    db.session.commit()
    return jsonify(diploma_awarded_schema.dump(diploma_awarded))


# ---- Student


@courses.route('/course_offerings/<int:person_id>', methods=['POST'])
@jwt_required
def add_student_to_course_offering(person_id):
    person = db.session.query(Person).filter_by(id=person_id).first()
    if person is None:
        return 'Person NOT in database', 404
    try:
        valid_student = student_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    course_offering = request.json['offeringId']
    studentInCO = db.session.query(Student).filter_by(
        student_id=person_id, offering_id=course_offering).first()  # Should only be one result in db
    if studentInCO is None:
        new_student = Student(**valid_student)

        db.session.add(new_student)
        db.session.commit()
        to_return = student_schema.dump(new_student)
        to_return['person'] = person_schema.dump(person)
        return jsonify(to_return), 201
    else:
        return 'Student already enrolled in course offering', 208


@courses.route('/course_offerings/<int:course_offering_id>/students')
@jwt_required
def read_all_course_offering_students(course_offering_id):
    """ This function lists all students by a specific course offering.
        Students are listed regardless of confirmed or active state. """
    co = db.session.query(Course_Offering).filter_by(
        id=course_offering_id).first()
    if co is None:
        return 'Course Offering NOT found', 404

    # Can be 0 or more students in a course offering
    students = db.session.query(Student, Person).filter_by(
        offering_id=course_offering_id).join(Person).all()

    student_list = []
    for i in students:
        s = student_schema.dump(i.Student)
        s['person'] = person_schema.dump(i.Person)
        student_list.append(s)
    return jsonify(student_list)


@courses.route('/students')
@jwt_required
def get_all_students():
    # Can be 0 or more people in database who are students
    people = db.session.query(Person).join(Student).all()
    to_return = []
    for i in people:
        p = person_schema.dump(i)
        p['diplomaList'] = []
        diplomas = i.diplomas_awarded
        for j in diplomas:
            d = db.session.query(Diploma).filter_by(id=j.diploma_id).first()
            d = diploma_schema.dump(d)
            d['diplomaIsActive'] = d.pop('active')
            p['diplomaList'].append(d)
        to_return.append(p)
    return jsonify(to_return)


@courses.route('/students/<int:student_id>')
@jwt_required
def read_one_student(student_id):
    """ Read transcript of a student that contains:
            - details of the student
            - diplomas awarded and in progress
            - courses required for diploma
            - list of courses taken and in progress
            - list of course offerings enrolled in for each course
    """
    result = db.session.query(Student, Person, Course_Offering, Course) \
        .filter_by(student_id=student_id).join(Person, Course_Offering, Course) \
        .all()
    if result == []:
        return 'Student not found', 404
    diplomas = []
    print(result)
    for da in result[0].Person.diplomas_awarded:
        diplomas.append(da.diplomas)
    result[0].Student.diplomaList = diplomas

    r = student_schema.dump(result[0].Student)
    r['person'] = person_schema.dump(result[0].Person)
    r['courses'] = []
    r['diplomaList'] = []
    for i in result[0].Person.diplomas_awarded:
        # Query to get diploma attributes
        d = db.session.query(Diploma).filter_by(id=i.diploma_id).first()
        # if d is None: #only hit this in the case where a person has an invalid diploma registered to them.
        #     return 'Diploma not found', 404
        d = diploma_schema.dump(d)
        d['diplomaIsActive'] = d.pop('active')
        # Query to find when award was given or if in progress (null value)
        award_query = db.session.query(DiplomaAwarded) \
            .filter_by(person_id=r['person']['id'], diploma_id=i.diploma_id) \
            .first()
        award_query = diploma_awarded_schema.dump(award_query)
        d['when'] = award_query['when']
        # Add all attributes to diplomaList
        r['diplomaList'].append(d)

    # The following adds all the courses associated with each diploma into a list
    for diploma in r['diplomaList']:
        # Get all courses associated with diploma
        diploma_query = db.session.query(DiplomaCourse).filter_by(
            diploma_id=diploma['id']).all()
        # Create a list of courses associated for each diploma
        diploma['courses'] = []
        for course in diploma_query:
            # Query course objects by courses associated with diploma
            course_query = db.session.query(
                Course).filter_by(id=course.course_id).first()
            course_query = course_schema.dump(course_query)
            course_query['id'] = course.course_id
            course_query['name'] = course_query['name']
            course_query.pop('description')
            course_query.pop('active')
            # Add course object details to list of courses for each diploma
            diploma['courses'].append(course_query)

        # Add courseCompleted attribute to each course object
        for course in diploma['courses']:
            # Query to see if course completion entry exists
            completion_query = db.session.query(CourseCompletion).filter_by(
                course_id=course['id'], person_id=r['person']['id']).first()
            completion_query = course_completion_schema.dump(completion_query)
            if completion_query:  # If the student has completed the course
                course['courseCompleted'] = True
            else:  # Student has not completed the course
                course['courseCompleted'] = False

    # For each person entry (enrolled in one or many courses)
    for i in result:
        # Add each course associated with course offerings enrolled
        r['courses'].append(course_schema.dump(i.Course))
    for i in r['courses']:
        i['courseOfferings'] = []
        # Query to see if course completion entry exists
        completion_query = db.session.query(CourseCompletion).filter_by(
            course_id=i['id'], person_id=r['person']['id']).first()
        completion_query = course_completion_schema.dump(completion_query)
        if completion_query:  # If the student has completed the course
            i['courseCompleted'] = True
        else:  # Student has not completed the course
            i['courseCompleted'] = False

        for j in result:
            if (j.Course_Offering.course_id == i['id']):
                co = course_offering_schema.dump(j.Course_Offering)
                co['courseIsActive'] = i['active']
                co['courseOfferingIsActive'] = co.pop('active')
                co.pop('id')
                co.pop('courseId')
                i['courseOfferings'].append(co)
    return jsonify(r)


@courses.route('/students/<int:student_id>', methods=['PATCH'])
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


# ---- Course_Completion


@courses.route('/courses/<int:courses_id>/course_completion', methods=['POST'])
@jwt_required
def create_course_completion(courses_id):
    """ Create and add course completion entry for a person. Requires path to contain
    valid courses_id and person_id in json request. """

    try:
        valid_course_completion = course_completion_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    person_id = request.json['personId']

    # Query into DB to ensure person is enrolled in a course offering with course_id
    personEnrolled = db.session.query(Person, Student, Course_Offering, Course) \
        .filter_by(id=person_id).join(Student, Course_Offering) \
        .filter_by(course_id=courses_id).join(Course) \
        .first()

    # Query into DB to ensure person has not already completed the course
    personCompleted = db.session.query(CourseCompletion) \
        .filter_by(course_id=courses_id, person_id=person_id) \
        .first()

    if personEnrolled is None:
        return jsonify(f'Person #{person_id} is not enrolled in any course offerings with course #{courses_id}.'), 404
    elif personCompleted:
        return jsonify(f'Entry for Person #{person_id} with completed course #{courses_id} already exists.'), 403
    else:
        # Create and add course completion entry for person
        new_course_completion = CourseCompletion(
            **{'person_id': person_id, 'course_id': courses_id})
        db.session.add(new_course_completion)
        db.session.commit()
        return jsonify(f'Person #{person_id} has successfully completed course #{courses_id}.'), 201


@courses.route('/courses/<int:courses_id>/course_completion', methods=['DELETE'])
@jwt_required
def delete_course_completion(courses_id):
    person_id = request.json['personId']
    course_completion = db.session.query(CourseCompletion) \
        .filter_by(course_id=courses_id, person_id=person_id).first()

    # If there is an entry in DB for course and person, then delete
    if course_completion is not None:
        db.session.delete(course_completion)
        db.session.commit()
        return 'Course completion successfully deleted', 200
    else:
        return jsonify(
            f'Cannot remove non-existing entry. Person #{person_id} with completed course #{courses_id} DNE.'), 404


# ---- ClassMeeting

@courses.route('/course_offerings/<int:course_offering_id>/class_meetings', methods=['POST'])
@jwt_required
def create_class_meeting(course_offering_id):
    """ Create and add class meeting into course offering.

    Note: Python datetime obj violates ISO 8601 and does not add timezone.
    Don't worry about timezones for now. """
    try:
        valid_class_meeting = class_meeting_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    meetingInDB = db.session.query(ClassMeeting).filter_by(
        offering_id=course_offering_id,
        teacher_id=valid_class_meeting['teacher_id'],
        when=valid_class_meeting['when']).first()

    # If a class meeting for a course offering DNE
    if meetingInDB is None:
        # Create and add new class meeting to course offering
        new_class_meeting = ClassMeeting(**valid_class_meeting)
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
    """ Read all class meetings associtated with a course offering """
    result = db.session.query(ClassMeeting).filter_by(
        offering_id=course_offering_id).all()
    result = class_meeting_schema.dump(result, many=True)

    return jsonify(result)


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>')
@jwt_required
def read_one_class_meeting(course_offering_id, class_meeting_id):
    """ Read data from a specific class_meeting entry """
    result = db.session.query(ClassMeeting).filter_by(
        id=class_meeting_id, offering_id=course_offering_id).first()
    if result is None:
        return 'Specified class meeting does not exist for this course offering', 404
    result = class_meeting_schema.dump(result)

    return jsonify(result)


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>', methods=['PATCH'])
@jwt_required
def update_class_meeting(course_offering_id, class_meeting_id):
    """ Update attributes for a class meeting """
    class_meeting = db.session.query(ClassMeeting).filter_by(
        id=class_meeting_id, offering_id=course_offering_id).first()
    # Cannot update class meeting with offering_id that DNE
    if class_meeting is None:
        return "Class meeting not found", 404

    try:
        valid_class_meeting = class_meeting_schema.load(
            request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # Update existing class meeting with offering_id
    for key, val in valid_class_meeting.items():
        setattr(class_meeting, key, val)
    db.session.commit()
    return jsonify(class_meeting_schema.dump(class_meeting))


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>', methods=['DELETE'])
@jwt_required
def delete_class_meeting(course_offering_id, class_meeting_id):
    class_meeting = db.session.query(ClassMeeting).filter_by(
        id=class_meeting_id, offering_id=course_offering_id).first()
    class_attended = db.session.query(ClassAttendance).filter_by(
        class_id=class_meeting_id).first()

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


def add_attendance_to_meetings(json_meeting):
    """ Helper function applies attendance with student name to a class meeting.
        **NOTE**: The meeting must be a ClassMeetingSchema dumped object. """
    json_meeting['attendance'] = []
    attendance = db.session.query(ClassAttendance, Student, Person).filter_by(
        class_id=json_meeting['id']).join(Student).join(Person).all()
    for i in attendance:
        json_meeting['attendance'].append(
            {"classId": i.class_id, "studentId": i.student_id, "name": i.Person.full_name()})
    return json_meeting


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>/class_attendance', methods=['POST'])
@jwt_required
def add_class_attendance(course_offering_id, class_meeting_id):
    """ Create new entries of attendance """
    # assume a list of (valid) student id's // EX: [1, 2, 3, 4]
    class_meeting = db.session.query(
        ClassMeeting).filter_by(id=class_meeting_id).first()
    if class_meeting is None:
        return 'Class Meeting not found', 404
    new_attendance = []
    for i in request.json['attendance']:
        student = db.session.query(Student).filter_by(
            id=i, offering_id=course_offering_id).first()
        print(student)
        if student is None:
            continue  # Student isn't enrolled in course offering or doesn't exist
        student.attendance.append(class_meeting)
        new_attendance.append(student)
    db.session.add_all(new_attendance)
    db.session.commit()
    return jsonify(add_attendance_to_meetings(class_meeting_schema.dump(class_meeting)))


@courses.route('/course_offerings/<course_offering_id>/class_attendance')
@jwt_required
def read_one_class_attendance(course_offering_id):
    """ Get all attendance from a single course """
    meetings = class_meeting_schema.dump(db.session.query(
        ClassMeeting).filter_by(offering_id=course_offering_id).all(), many=True)
    if meetings == []:
        return 'Class Meetings NOT found for this course offering', 404
    for i in meetings:
        add_attendance_to_meetings(i)
    return jsonify(meetings)


@courses.route('/course_offerings/<course_offering_id>/<class_meeting_id>/class_attendance')
@jwt_required
def read_one_meeting_attendance(course_offering_id, class_meeting_id):
    """ Get attendance for a single class """
    meeting = class_meeting_schema.dump(db.session.query(ClassMeeting).filter_by(
        offering_id=course_offering_id, id=class_meeting_id).first())
    if meeting == {}:
        return 'Class Meeting NOT found', 404
    add_attendance_to_meetings(meeting)
    return jsonify(meeting)


@courses.route('/course_offerings/<int:course_offering_id>/<int:class_meeting_id>/class_attendance', methods=['PATCH'])
@jwt_required
def update_class_attendance(course_offering_id, class_meeting_id):
    # assume a list of valid student id's // EX: [1, 2, 4]
    current_attendance = class_attendance_schema.dump(db.session.query(
        ClassAttendance).filter_by(class_id=class_meeting_id).all(), many=True)
    class_meeting = db.session.query(
        ClassMeeting).filter_by(id=class_meeting_id).first()
    updated_attendance = []
    for i in request.json['attendance']:
        updated_attendance.append(
            {"classId": class_meeting_id, "studentId": i})
    updates = []
    # Delete missing
    for i in current_attendance:
        if i not in updated_attendance:
            student = db.session.query(Student).filter_by(
                id=i['studentId'], offering_id=course_offering_id).first()
            if student is None:
                continue  # Student isn't enrolled in course offering or doesn't exist
            student.attendance.remove(class_meeting)
            updates.append(student)

    # Now to add new things
    for i in updated_attendance:
        if i not in current_attendance:
            student = db.session.query(Student).filter_by(
                id=i['studentId'], offering_id=course_offering_id).first()
            if student is None:
                continue  # Student isn't enrolled in course offering or doesn't exist
            student.attendance.append(class_meeting)
            updates.append(student)

    db.session.add_all(updates)
    db.session.commit()  # Commit all new changes
    return jsonify(add_attendance_to_meetings(class_meeting_schema.dump(class_meeting)))


# ---- Image


@courses.route('/<course_id>/images/<image_id>', methods=['POST'])
@jwt_required
def add_course_images(course_id, image_id):
    course = db.session.query(Course).filter_by(id=course_id).first()
    image = db.session.query(Image).filter_by(id=image_id).first()

    course_image = db.session.query(ImageCourse).filter_by(
        course_id=course_id, image_id=image_id).first()

    if not course:
        return jsonify(f"Course with id #{course_id} does not exist."), 404

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    # If image is already attached to the course
    if course_image:
        return jsonify(f"Image with id#{image_id} is already attached to course with id#{course_id}."), 422
    else:
        new_entry = ImageCourse(
            **{'course_id': course_id, 'image_id': image_id})
        db.session.add(new_entry)
        db.session.commit()

    return jsonify(f"Image with id #{image_id} successfully added to Course with id #{course_id}."), 201


@courses.route('/<course_id>/images/<image_id>', methods=['PUT'])
@jwt_required
def put_course_images(course_id, image_id):
    # check for old image id in parameter list (?old=<id>)
    old_image_id = request.args['old']
    new_image_id = image_id

    if old_image_id == 'false':
        post_resp = add_course_images(course_id, new_image_id)
        return jsonify({'deleted': 'No image to delete', 'posted': str(post_resp[0].data, "utf-8")})
    else:
        del_resp = delete_course_image(course_id, old_image_id)
        post_resp = add_course_images(course_id, new_image_id)

        return jsonify({'deleted': del_resp[0], 'posted': str(post_resp[0].data, "utf-8")})


@courses.route('/<course_id>/images/<image_id>', methods=['DELETE'])
@jwt_required
def delete_course_image(course_id, image_id):
    course_image = db.session.query(ImageCourse).filter_by(
        course_id=course_id, image_id=image_id).first()

    if not course_image:
        return jsonify(f"Image with id #{image_id} is not assigned to Course with id #{course_id}."), 404

    db.session.delete(course_image)
    db.session.commit()

    # 204 codes don't respond with any content
    return 'Successfully removed image', 204

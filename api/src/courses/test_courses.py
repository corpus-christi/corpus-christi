import random
from datetime import datetime

import pytest
from faker import Faker
from flask import url_for

from .models import Course, CourseSchema, Course_Offering, CourseOfferingSchema, \
    Diploma, DiplomaSchema, Student, StudentSchema, \
    ClassMeeting, ClassMeetingSchema, DiplomaAwarded, DiplomaAwardedSchema, \
    ClassAttendance, CourseCompletion, CourseCompletionSchema
from ..images.create_image_data import create_test_images, create_images_courses
from ..images.models import Image, ImageCourse
from ..people.models import Person
from ..people.test_people import create_multiple_people
from ..places.models import Country, Location
from ..places.test_places import create_multiple_areas, \
    create_multiple_addresses, create_multiple_locations


def flip():
    # Return true or false randomly.
    return random.choice((True, False))


# --- Population Data

# --- Course


def course_object_factory():
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
        'name': "course: " + fake.sentence(nb_words=3),
        'description': "description: " + fake.paragraph(),
        'active': flip()
    }
    return course


def course_object_factory_active():
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
        'name': "course: " + fake.sentence(nb_words=3),
        'description': "description: " + fake.paragraph(),
        'active': True
    }
    return course


def course_object_factory_inactive():
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course = {
        'name': "course: " + fake.sentence(nb_words=3),
        'description': "description: " + fake.paragraph(),
        'active': False
    }
    return course


def create_multiple_courses(sqla, n=10):
    # Commits the number of courses to the DB.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()


def create_multiple_courses_active(sqla, n=10):
    # Commits the number of courses to the DB.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_active())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()


def create_multiple_courses_inactive(sqla, n=10):
    # Commits the number of courses to the DB.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_schema = CourseSchema()
    new_courses = []
    for i in range(n):
        valid_course = course_schema.load(course_object_factory_inactive())
        course_model = Course(**valid_course)
        new_courses.append(course_model)
    sqla.add_all(new_courses)
    sqla.commit()


# --- Course_Offering


def course_offerings_object_factory(course_id):
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
        'maxSize': random.randint(1, 100),
        'description': "course offering: " + fake.paragraph(),
        'active': flip(),
        'courseId': course_id
    }
    return course_offerings


def course_offerings_object_factory_active(course_id):
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
        'maxSize': random.randint(1, 100),
        'description': "course offering: " + fake.paragraph(),
        'active': True,
        'courseId': course_id
    }
    return course_offerings


def course_offerings_object_factory_inactive(course_id):
    # Cook up a fake course.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_offerings = {
        'maxSize': random.randint(1, 100),
        'description': "course offering: " + fake.paragraph(),
        'active': False,
        'courseId': course_id
    }
    return course_offerings


def create_multiple_course_offerings(sqla, n=3):
    # Commits the number of course offering to the DB.
    courses = sqla.query(Course).all()
    if not courses:
        create_multiple_courses(sqla, random.randint(3, 6))
        courses = sqla.query(Course).all()
    course_offerings_schema = CourseOfferingSchema()
    new_course_offerings = []
    for i in range(n):
        c = random.randint(1, len(courses))
        valid_course_offering = course_offerings_schema.load(
            course_offerings_object_factory(c))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()


def create_multiple_course_offerings_active(sqla, n=3):
    # Commits the number of course offering to the DB.
    course = sqla.query(Course).first()
    if not course:
        create_multiple_courses(sqla, random.randint(3, 6))
        course = sqla.query(Course).all()
    course_offerings_schema = CourseOfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(
            course_offerings_object_factory_active(course.id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()


def create_multiple_course_offerings_inactive(sqla, n=3):
    # Commits the number of course offering to the DB.
    course = sqla.query(Course).first()
    if not course:
        create_multiple_courses(sqla, random.randint(3, 6))
        course = sqla.query(Course).all()
    course_offerings_schema = CourseOfferingSchema()
    new_course_offerings = []
    for i in range(n):
        valid_course_offering = course_offerings_schema.load(
            course_offerings_object_factory_inactive(course.id))
        new_course_offerings.append(Course_Offering(**valid_course_offering))
    sqla.add_all(new_course_offerings)
    sqla.commit()


# --- Prerequisites


def prerequisite_object_factory(course_id, prereq_id):
    # Cook up a fake prerequisite.
    prerequisites = {
        'courseId': course_id,
        'prereqId': prereq_id
    }
    return prerequisites


def create_multiple_prerequisites(sqla):
    # Commits the courses - 1 number of prerequisites to the DB.
    courses = sqla.query(Course).all()
    if not courses:
        create_multiple_courses(sqla, random.randint(3, 6))
        courses = sqla.query(Course).all()
    new_prerequisites = []
    for i in range(len(courses) - 1):
        courses[i].prerequisites.append(courses[i + 1])
        new_prerequisites.append(courses[i])
    sqla.add_all(new_prerequisites)
    sqla.commit()


# --- Diploma


def courses_diploma_object_factory(num_courses):
    # Cook up a fake diploma.
    fake = Faker()  # Use a generic one; others may not have all methods.
    course_diploma = {
        'name': "diploma name: " + fake.sentence(nb_words=4),
        'description': "diploma description: " + fake.paragraph(),
        'active': flip(),
    }
    return course_diploma


def create_multiple_diplomas(sqla, n=20):
    # Commits the number of diplomas to the DB.
    courses = sqla.query(Course).all()
    if not courses:
        create_multiple_courses(sqla, random.randint(3, 6))
        courses = sqla.query(Course).all()
    course_diploma_schema = DiplomaSchema()
    new_courses = []
    for i in range(n):
        valid_course_diploma = course_diploma_schema.load(
            courses_diploma_object_factory(20))
        diploma = Diploma(**valid_course_diploma)
        courses[i % len(courses)].diplomas.append(diploma)
    sqla.add_all(new_courses)
    sqla.commit()


# --- Student


def student_object_factory(offering_id, student_id):
    # Cook up a fake student
    fake = Faker()
    course_student = {
        'studentId': student_id,
        'offeringId': offering_id,
        'confirmed': flip(),
        'active': flip()
    }
    return course_student


def create_multiple_students(sqla, n=6, course_offering_id=None):
    # Commits the number of students to the DB.
    students = sqla.query(Person).all()
    if not students:
        create_multiple_students(sqla, random.randint(3, 6))
        students = sqla.query(Student).all()
    course_offering = sqla.query(Course_Offering).all()
    if not course_offering:
        create_multiple_course_offerings(sqla, random.randint(3, 6))
        course_offering = sqla.query(Course_Offering).all()
    course_students_schema = StudentSchema()
    new_students = []
    for i in range(n):
        if not course_offering_id:
            valid_student = course_students_schema.load(student_object_factory(
                course_offering[i % len(course_offering)].id, students[i % len(students)].id))
        else:
            valid_student = course_students_schema.load(student_object_factory(
                course_offering_id, students[i % len(students)].id))
        student = Student(**valid_student)
        new_students.append(student)
    sqla.add_all(new_students)
    sqla.commit()


# --- Diploma_Award


def diploma_award_object_factory(diploma_id, people_id):
    # Cook up a fake diploma award
    fake = Faker()
    diploma_award = {
        'personId': people_id,
        'diplomaId': diploma_id,
        'when': str(fake.past_date(start_date="-30d"))
    }
    return diploma_award


def create_diploma_awards(sqla, n):
    # Commits the number of diploma awards to the DB.
    people = sqla.query(Person).all()
    if not people:
        create_multiple_people(sqla, random.randint(3, 6))
        people = sqla.query(Person).all()
    diplomas = sqla.query(Diploma).all()
    if not diplomas:
        create_multiple_diplomas(sqla, random.randint(3, 6))
        diplomas = sqla.query(Person).all()
    diploma_award_schema = DiplomaAwardedSchema()
    new_diploma_awards = []
    for i in range(n):
        for person in people:
            diploma = diplomas[i]
            valid_diploma_awarded = diploma_award_schema.load(
                diploma_award_object_factory(diploma.id, person.id))
            new_diploma_awards.append(DiplomaAwarded(**valid_diploma_awarded))
    sqla.add_all(new_diploma_awards)
    sqla.commit()


def course_completion_object_factory(person_id, course_id):
    # Cook up a fake course completion
    course_completion = {
        'personId': person_id,
        'courseId': course_id
    }
    return course_completion


def create_course_completion(sqla, n):
    # Commits the number of course completions to the DB.
    people = sqla.query(Person).all()
    if not people:
        create_multiple_people(sqla, random.randint(3, 6))
        people = sqla.query(Person).all()
    courses = sqla.query(Course).all()
    if not courses:
        create_multiple_courses(sqla, random.randint(3, 6))
        courses = sqla.query(Course).all()
    course_completion_schema = CourseCompletionSchema()
    new_course_completion = []
    for person in people:
        course = courses[random.randint(0, len(courses) - 1)]
        valid_course_completion = course_completion_schema.load(
            course_completion_object_factory(person.id, course.id))
        person.completions.append(CourseCompletion(**valid_course_completion))
        new_course_completion.append(person)
    sqla.add_all(new_course_completion)
    sqla.commit()


# --- ClassMeeting

def class_meeting_object_factory(teacher_id, offering_id, location_id=1):
    # Cook up a fake class meeting
    fake = Faker()
    class_meeting = {
        'offeringId': offering_id,
        'teacherId': teacher_id,
        'when': str(fake.future_datetime(end_date="+30d")),
        'locationId': location_id,
    }
    return class_meeting


def create_class_meetings(sqla, n=6):
    # Commits the number of class meetings to the DB.
    people = sqla.query(Person).all()
    if not people:
        create_multiple_people(sqla, random.randint(3, 6))
        people = sqla.query(Person).all()
    course_offerings = sqla.query(Course_Offering).all()
    if not course_offerings:
        create_multiple_course_offerings(sqla, random.randint(3, 6))
        course_offerings = sqla.query(Course_Offering).all()
    locations = sqla.query(Location).all()
    if not locations:
        create_multiple_locations(sqla, random.randint(3, 6))
        locations = sqla.query(Location).all()
    class_meeting_schema = ClassMeetingSchema()
    new_class_meetings = []
    for i in range(n):
        teacher = people[random.randint(0, len(people) - 1)].id
        offering = course_offerings[random.randint(
            0, len(course_offerings) - 1)].id
        location = locations[random.randint(0, len(locations) - 1)].id

        valid_class_meeting = class_meeting_schema.load(
            class_meeting_object_factory(teacher, offering, location))
        class_meeting = ClassMeeting(**valid_class_meeting)
        new_class_meetings.append(class_meeting)
    sqla.add_all(new_class_meetings)
    sqla.commit()


def create_class_attendance(sqla, n):
    # Commits the number of class attendances to the DB.
    students = sqla.query(Student).all()
    if not students:
        create_multiple_students(sqla, random.randint(3, 6))
        students = sqla.query(Student)
    class_meetings = sqla.query(ClassMeeting).all()
    if not class_meetings:
        create_multiple_class_meetings(sqla, random.randint(3, 6))
        class_meetings = sqla.query(ClassMeeting).all()
    new_class_attendance = []
    for i in range(n):
        class_meeting = class_meetings[random.randint(
            0, len(class_meetings) - 1)]
        student = students[i]
        # while class_meeting in student.attendance:
        #     student = students[random.randint(0, len(students)-1)]
        student.attendance.append(class_meeting)
        new_class_attendance.append(student)
    sqla.add_all(new_class_attendance)
    sqla.commit()


# ---- Course

# Test course creation


def test_create_course(auth_client):
    # Test creating invalid course
    # GIVEN invalid course to put in database
    broken_course = {}
    # WHEN database queried
    resp = auth_client.post(
        url_for('courses.create_course'), json=broken_course)
    # THEN assert exception thrown
    assert resp.status_code == 422
    # Test creating valid course
    # GIVEN course entry to put in database
    count = random.randint(8, 19)
    # WHEN database does not contain entry
    for i in range(count):
        resp = auth_client.post(
            url_for('courses.create_course'), json=course_object_factory())
        assert resp.status_code == 201
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(Course).count() == count


# Test getting all courses from the database
def test_read_all_courses(auth_client):
    # Test with empty database
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_courses'))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN existing (active and inactive) courses in database
    count = random.randint(3, 11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_prerequisites(auth_client.sqla)
    create_multiple_course_offerings(auth_client.sqla, 5)
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_all_courses'))
    # THEN assert all entries from database are called
    assert resp.status_code == 200
    assert len(resp.json) == count


# Test getting courses by active state


def test_read_active_state_of_courses(auth_client):
    # GIVEN existing and active/inactive courses
    count_active = random.randint(3, 11)
    create_multiple_courses_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3, 11)
    create_multiple_courses_inactive(auth_client.sqla, count_inactive)
    # Test listing all active courses
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_of_courses', active_state='active'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_active
    # Test listing all inactive courses
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_of_courses', active_state='inactive'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_inactive
    # Test listing courses with invalid state
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_of_courses', active_state='garbage'))
    # THEN assert error code
    assert resp.status_code == 404


# Test reading a single course from the database


def test_read_one_course(auth_client):
    # Test with invalid course
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_one_course', course_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN one course in the database
    count = random.randint(3, 11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_prerequisites(auth_client.sqla)
    create_multiple_course_offerings(auth_client.sqla, 5)
    # WHEN call to database
    courses = auth_client.sqla.query(Course).all()
    # THEN assert entry called is only entry returned
    for course in courses:
        resp = auth_client.get(
            url_for('courses.read_one_course', course_id=course.id))
        # THEN we find a matching class
        assert resp.status_code == 200
        assert resp.json['name'] == course.name
        assert resp.json['description'] == course.description
        assert resp.json['active'] == course.active


def test_update_course(auth_client):
    # Test with invalid course
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_course', course_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN active or inactive course in database
    count = random.randint(3, 11)
    create_multiple_courses(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    # WHEN course information updated
    for course in courses:
        resp = auth_client.patch(url_for('courses.update_course', course_id=course.id),
                                 json={'name': 'test_name',
                                       'description': 'test_descr', 'active': False})
        # THEN assert course reflects new detail(s)
        assert resp.status_code == 200
        assert resp.json['name'] == 'test_name'
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False


# ---- Prerequisite

# Test that prerequisites can be added


def test_create_prerequisite(auth_client):
    # Test with invalid course
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.post(
        url_for('courses.create_prerequisite', course_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN existing and available course in database
    count = random.randint(2, 13)
    create_multiple_courses(auth_client.sqla, count)
    courses = auth_client.sqla.query(Course).all()
    course = courses[0]
    prereq_ids = []
    for prereq in courses:
        prereq_ids.append(prereq.id)
    # WHEN course requires previous attendance to another course
    resp = auth_client.post(url_for('courses.create_prerequisite', course_id=course.id),
                            json={'prerequisites': prereq_ids})
    assert resp.status_code == 201
    # THEN asssert course is prerequisite
    course = auth_client.sqla.query(Course).all()[0]
    for i in range(len(prereq_ids) - 1):
        assert course.prerequisites[i].id == prereq_ids[i + 1]


# This will test getting all prerequisites for all courses


def test_read_all_prerequisites(auth_client):
    # Test with empty database
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_prerequisites'))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN existing and available course in database
    count_courses = random.randint(3, 15)
    count_prereqs = count_courses - 1
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    # WHEN that course has prerequisites
    resp = auth_client.get(url_for('courses.read_all_prerequisites'))
    assert resp.status_code == 200
    # THEN assert all prereq's are listed
    assert len(resp.json) == count_prereqs


# This will test getting prerequistes for one course


def test_read_one_course_prerequisites(auth_client):
    # Test with invalid course
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(
        url_for('courses.read_one_course_prerequisites', course_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN course in database
    count_courses = random.randint(3, 15)
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    # WHEN that course has prerequisites
    courses = auth_client.sqla.query(Course).all()
    # THEN list all prerequisites of given course
    for course in courses:
        resp = auth_client.get(
            url_for('courses.read_one_course_prerequisites', course_id=course.id))
        assert resp.status_code == 200
        for i in range(len(resp.json)):
            assert resp.json[i]['id'] == course.prerequisites[i].id
            assert resp.json[i]['name'] == course.prerequisites[i].name
            assert resp.json[i]['description'] == course.prerequisites[i].description
            assert resp.json[i]['active'] == course.prerequisites[i].active


def test_update_prerequisite(auth_client):
    # Test with invalid course
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_prerequisite', course_id=1),
                             json={'prerequisites': [1]})
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN an existing and available course with an existing prereq
    count_courses = random.randint(3, 13)
    create_multiple_courses(auth_client.sqla, count_courses)
    create_multiple_prerequisites(auth_client.sqla)
    courses = auth_client.sqla.query(Course).all()
    # WHEN new prereq for existing course is required
    for course in courses:
        resp = auth_client.patch(url_for('courses.update_prerequisite', course_id=course.id),
                                 json={'prerequisites': [1]})
        assert resp.status_code == 200
    # THEN existing course has new prereq in place of existing prereq
    courses = auth_client.sqla.query(Course).all()
    for course in courses:
        if course.id == 1:
            continue
        assert course.prerequisites[0].id == 1


# ---- Course_Offering


def test_create_course_offering(auth_client):
    # Test creating invalid course offering
    # GIVEN invalid course offering to put in database
    broken_course_offering = {}
    # WHEN database queried
    resp = auth_client.post(
        url_for('courses.create_course_offering'), json=broken_course_offering)
    # THEN assert exception thrown
    assert resp.status_code == 422
    # Test creating valid course offering
    # GIVEN an existing course
    count = random.randint(8, 19)
    create_multiple_courses(auth_client.sqla, 1)
    course = auth_client.sqla.query(Course).first()
    # WHEN one or more courses need a section to offer
    for i in range(count):
        resp = auth_client.post(url_for(
            'courses.create_course_offering'), json=course_offerings_object_factory(course.id))
        assert resp.status_code == 201
    # THEN create new course section
    assert auth_client.sqla.query(Course_Offering).count() == count


def test_read_all_course_offerings(auth_client):
    # GIVEN existing (active and inactive) course offerings
    create_multiple_courses(auth_client.sqla, 1)
    count = random.randint(8, 19)
    create_multiple_course_offerings(auth_client.sqla, count)
    # WHEN all sections needed
    resp = auth_client.get(url_for('courses.read_all_course_offerings'))
    # THEN list all course sections
    assert len(resp.json) == count


def test_read_active_state_course_offerings(auth_client):
    # GIVEN existing active/inactive course offerings
    create_multiple_courses(auth_client.sqla, 1)
    count_active = random.randint(3, 11)
    create_multiple_course_offerings_active(auth_client.sqla, count_active)
    count_inactive = random.randint(3, 11)
    create_multiple_course_offerings_inactive(auth_client.sqla, count_inactive)
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_course_offerings', active_state='active'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_active
    # Test listing all inactive courses
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_course_offerings', active_state='inactive'))
    # THEN assert all active courses are listed
    assert resp.status_code == 200
    assert len(resp.json) == count_inactive
    # Test listing courses with invalid state
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_active_state_course_offerings', active_state='garbage'))
    # THEN assert error code
    assert resp.status_code == 404


def test_read_one_course_offering(auth_client):
    # GIVEN an existing course
    create_multiple_courses(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_course_offerings(auth_client.sqla, count)
    # WHEN one course section needed
    course_offerings = auth_client.sqla.query(Course_Offering).all()
    # THEN list one course section of course
    for course_offering in course_offerings:
        resp = auth_client.get(url_for(
            'courses.read_one_course_offering', course_offering_id=course_offering.id))
        assert resp.status_code == 200
        assert resp.json['maxSize'] == course_offering.max_size
        assert resp.json['description'] == course_offering.description
        assert resp.json['active'] == course_offering.active
        assert resp.json['courseId'] == course_offering.course_id


def test_update_course_offering(auth_client):
    # Test with invalid course offering
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(
        url_for('courses.update_course_offering', course_offering_id=555))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN an existing (active or inactive) course offering
    create_multiple_courses(auth_client.sqla, 1)
    count = random.randint(3, 11)
    create_multiple_course_offerings(auth_client.sqla, count)
    course_offerings = auth_client.sqla.query(Course_Offering).all()
    # WHEN course offering needs to update existing information
    for course_offering in course_offerings:
        resp = auth_client.patch(url_for('courses.update_course_offering', course_offering_id=course_offering.id),
                                 json={'maxSize': 1, 'description': 'test_descr', 'active': False})
        # THEN assert changes to course offering reflect update
        assert resp.status_code == 200
        assert resp.json['maxSize'] == 1
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False


# ---- Diploma


def test_create_diploma(auth_client):
    # Test with invalid diploma
    # GIVEN invalid diploma to add
    create_multiple_courses(auth_client.sqla, 10)
    broken_diploma = {}
    # WHEN database queried
    resp = auth_client.post(
        url_for('courses.create_diploma'), json=broken_diploma)
    # THEN assert error code
    assert resp.status_code == 422
    # Test for good diploma
    # GIVEN some existing courses
    # WHEN we create a diploma and add courses to add
    diploma = courses_diploma_object_factory(10)
    diploma['courseList'] = [1, 2, 3]
    resp = auth_client.post(url_for('courses.create_diploma'), json=diploma)
    # THEN the diploma is added to the db
    assert resp.status_code == 201
    assert auth_client.sqla.query(Diploma).count() == 1


def test_read_all_diplomas(auth_client):
    # Test with empty database
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_diplomas'))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN 50 courses and 15 diplomas
    create_multiple_courses(auth_client.sqla, 50)
    create_multiple_diplomas(auth_client.sqla, 15)
    setup_dependencies_of_student(auth_client, 15)
    create_multiple_students(auth_client.sqla, 15)
    create_diploma_awards(auth_client.sqla, 15)
    # WHEN we read the diplomas
    resp = auth_client.get(url_for('courses.read_all_diplomas'))
    # THEN we should receive 15 diplomas
    assert resp.status_code == 200
    assert len(resp.json) == 15


def test_read_one_diploma(auth_client):
    # Test with invalid diploma
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_one_diploma', diploma_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN one course in the database
    count = random.randint(3, 11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, count)
    setup_dependencies_of_student(auth_client, count)
    create_multiple_students(auth_client.sqla, count)
    create_diploma_awards(auth_client.sqla, count)
    # WHEN call to database
    diplomas = auth_client.sqla.query(Diploma).all()
    # THEN assert entry called is only entry returned
    for diploma in diplomas:
        resp = auth_client.get(
            url_for('courses.read_one_diploma', diploma_id=diploma.id))
        # THEN we find a matching class
        assert resp.status_code == 200
        assert resp.json['name'] == diploma.name
        assert resp.json['description'] == diploma.description
        assert resp.json['active'] == diploma.active


def test_update_diploma(auth_client):
    # Test with invalid diploma
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for('courses.update_diploma', diploma_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN diploma in database
    count = random.randint(3, 11)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, count)
    diplomas = auth_client.sqla.query(Course).all()
    # WHEN diploma information updated
    for diploma in diplomas:
        resp = auth_client.patch(url_for('courses.update_diploma', diploma_id=diploma.id),
                                 json={'name': 'test_name', 'description': 'test_descr', 'active': False,
                                       'courseList': [1, 2, 3]})
        # THEN assert diploma reflects new detail(s)
        assert resp.status_code == 200
        assert resp.json['name'] == 'test_name'
        assert resp.json['description'] == 'test_descr'
        assert resp.json['active'] == False
        for i in range(len(resp.json['courseList'])):
            assert resp.json['courseList'][i]['id'] == i + 1
    # Test without fake attribute
    # GIVEN diploma in database
    # WHEN some fake attribute is to be updated
    resp = auth_client.patch(url_for('courses.update_diploma', diploma_id=diploma.id),
                             json={'fake_attr': 'fake_attr'})
    # THEN assert error code
    assert resp.status_code == 422


def test_add_course_to_diploma(auth_client):
    # Test with populated database
    # GIVEN courses and diplomas in database
    count = random.randint(3, 15)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, 1)
    diploma = auth_client.sqla.query(Diploma).first()
    diploma_courses = []
    diploma_courses.append(diploma.courses)
    create_multiple_courses(auth_client.sqla, 1)
    new_course = auth_client.sqla.query(Course).all()[count]
    # WHEN query database
    resp = auth_client.put(url_for(
        'courses.add_course_to_diploma', diploma_id=diploma.id, course_id=new_course.id))
    # THEN assert course is now added
    diploma_courses.append(new_course.id)
    assert resp.status_code == 200
    assert len(resp.json['courseList']) == len(diploma_courses)
    # Add course already in diploma
    # GIVEN course already in diploma's courses
    # WHEN asked to add it again
    resp = auth_client.put(url_for(
        'courses.add_course_to_diploma', diploma_id=diploma.id, course_id=new_course.id))
    # THEN assert error code
    assert resp.status_code == 409


def test_remove_course_from_diploma(auth_client):
    # Test with populated database
    # GIVEN courses and diplomas in database
    count = random.randint(3, 15)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, 1)
    diploma = auth_client.sqla.query(Diploma).first()
    diploma_courses = []
    diploma_courses.append(diploma.courses)
    course_to_remove = diploma.courses[0]
    # WHEN query database
    resp = auth_client.delete(url_for(
        'courses.remove_course_from_diploma', diploma_id=diploma.id, course_id=course_to_remove.id))
    # THEN assert course is now removed
    assert resp.status_code == 200
    diploma = auth_client.sqla.query(Diploma).first()
    assert len(diploma.courses) == len(diploma_courses) - 1

    # Remove course not in diploma
    # GIVEN course not in diploma's courses
    # WHEN asked to reomve it again
    resp = auth_client.delete(url_for(
        'courses.remove_course_from_diploma', diploma_id=diploma.id, course_id=course_to_remove.id))
    # THEN assert error code
    assert resp.status_code == 404

    # Attempt to remove course from diploma that has been awarded
    # GIVEN diploma that has been awarded
    create_multiple_people(auth_client.sqla, 1)
    create_diploma_awards(auth_client.sqla, 1)
    auth_client.put(url_for('courses.add_course_to_diploma',
                            diploma_id=diploma.id, course_id=course_to_remove.id))
    resp = auth_client.delete(url_for(
        'courses.remove_course_from_diploma', diploma_id=diploma.id, course_id=course_to_remove.id))
    assert resp.status_code == 403


def test_activate_diploma(auth_client):
    # Test with invalid diploma
    # GIVEN empty database
    # WHEN asked to deactivate diploma
    resp = auth_client.patch(url_for('courses.activate_diploma', diploma_id=1))
    # THEN assert error code
    assert resp.status_code == 404

    # Test with populated database
    # GIVEN diploma in database
    count = random.randint(3, 15)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, 1)
    diploma = auth_client.sqla.query(Diploma).first()
    auth_client.patch(
        url_for('courses.deactivate_diploma', diploma_id=diploma.id))
    # WHEN requested to activate
    resp = auth_client.patch(
        url_for('courses.activate_diploma', diploma_id=diploma.id))
    # THEN assert it worked
    assert resp.status_code == 200
    assert auth_client.sqla.query(Diploma).first().active == True


def test_deactivate_diploma(auth_client):
    # Test with invalid diploma
    # GIVEN empty database
    # WHEN asked to deactivate diploma
    resp = auth_client.patch(
        url_for('courses.deactivate_diploma', diploma_id=1))
    # THEN assert error code
    assert resp.status_code == 404

    # Test with populated database
    # GIVEN diploma in database
    count = random.randint(3, 15)
    create_multiple_courses(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, 1)
    diploma = auth_client.sqla.query(Diploma).first()
    # WHEN requested to deactivate
    resp = auth_client.patch(
        url_for('courses.deactivate_diploma', diploma_id=diploma.id))
    # THEN assert it worked
    assert resp.status_code == 200
    assert auth_client.sqla.query(Diploma).first().active == False


# ---- DiplomaAwarded


def test_create_diploma_awarded(auth_client):
    # Test creating invalid diploma awarded
    # GIVEN invalid diploma awarded to put in database
    broken_diploma_awarded = {}
    # WHEN database queried
    resp = auth_client.post(
        url_for('courses.create_diploma_awarded'), json=broken_diploma_awarded)
    # THEN assert exception thrown
    assert resp.status_code == 422

    # Test creating valid diploma awarded
    # GIVEN diploma awarded to put in database
    count = random.randint(8, 19)
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    create_multiple_diplomas(auth_client.sqla, count)
    # WHEN database does not contain entry
    for i in range(count):
        resp = auth_client.post(url_for(
            'courses.create_diploma_awarded'), json=diploma_award_object_factory(i + 1, 1))
        assert resp.status_code == 201
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(DiplomaAwarded).count() == count

    # Test creating an already existing diploma awarded
    resp = auth_client.post(url_for(
        'courses.create_diploma_awarded'), json=diploma_award_object_factory(1, 1))
    assert resp.status_code == 409


def test_read_all_diplomas_awarded(auth_client):
    # Test with empty database
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_all_diplomas_awarded'))
    # THEN assert error code
    assert resp.status_code == 404

    # Test with populated database
    # GIVEN existing (active and inactive) courses in database
    count = random.randint(3, 11)
    setup_dependencies_of_student(auth_client, count)
    create_multiple_students(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, count)
    create_diploma_awards(auth_client.sqla, count)
    # WHEN call to database
    resp = auth_client.get(url_for('courses.read_all_diplomas_awarded'))
    # THEN assert all entries from database are called
    assert resp.status_code == 200
    assert len(resp.json) == count * count


def test_read_one_diploma_awarded(auth_client):
    # Test with invalid diploma awarded
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(
        url_for('courses.read_one_diploma_awarded', person_id=1, diploma_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN one course in the database
    count = random.randint(3, 11)
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    create_multiple_diplomas(auth_client.sqla, count)
    create_diploma_awards(auth_client.sqla, count)
    # WHEN call to database
    diplomas_awarded = auth_client.sqla.query(DiplomaAwarded).all()
    # THEN assert entry called is only entry returned
    for diploma_awarded in diplomas_awarded:
        resp = auth_client.get(url_for(
            'courses.read_one_diploma_awarded', diploma_id=diploma_awarded.diploma_id, person_id=1))
        # THEN we find a matching class
        assert resp.status_code == 200
        assert resp.json['personId'] == diploma_awarded.person_id
        assert resp.json['diplomaId'] == diploma_awarded.diploma_id
        assert datetime.strptime(
            resp.json['when'], '%Y-%m-%d').date() == diploma_awarded.when


def test_update_diploma_awarded(auth_client):
    # Test with invalid diploma awarded
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(
        url_for('courses.update_diploma_awarded', diploma_id=1, person_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN class meeting in database
    count = random.randint(3, 11)
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    create_multiple_diplomas(auth_client.sqla, count)
    create_diploma_awards(auth_client.sqla, count)
    diplomas_awarded = auth_client.sqla.query(DiplomaAwarded).all()
    fake = Faker()
    time = str(fake.past_date(start_date="-30d"))
    # WHEN course information updated
    for diploma_awarded in diplomas_awarded:
        resp = auth_client.patch(url_for('courses.update_diploma_awarded', diploma_id=diploma_awarded.diploma_id,
                                         person_id=diploma_awarded.person_id),
                                 json={'when': time})
        # THEN assert meeting reflectts new detail(s)
        assert resp.status_code == 200
        assert datetime.strptime(
            resp.json['when'], '%Y-%m-%d') == datetime.strptime(time, '%Y-%m-%d')
    # Test with fake attribute
    # GIVEN diploma awarded in database
    # WHEN some fake attribute is to be updated
    resp = auth_client.patch(url_for('courses.update_diploma_awarded', diploma_id=diploma_awarded.diploma_id,
                                     person_id=diploma_awarded.person_id),
                             json={'fake_attr': 'fake_attr'})
    # THEN assert error code
    assert resp.status_code == 422


def test_delete_diploma_awarded(auth_client):
    # Test with invalid diploma awarded
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.delete(
        url_for('courses.delete_diploma_awarded', diploma_id=1, person_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN diploma awarded in database
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    create_multiple_diplomas(auth_client.sqla, 1)
    create_diploma_awards(auth_client.sqla, 1)
    diploma_awarded = auth_client.sqla.query(DiplomaAwarded).first()
    # WHEN deleted
    resp = auth_client.delete(url_for('courses.delete_diploma_awarded',
                                      diploma_id=diploma_awarded.diploma_id, person_id=diploma_awarded.person_id))
    # THEN assert it is gone
    assert resp.status_code == 200
    assert auth_client.sqla.query(DiplomaAwarded).all() == []


# ---- Student

def setup_dependencies_of_student(auth_client, n):
    create_multiple_people(auth_client.sqla, n)
    create_multiple_courses_active(auth_client.sqla, n)
    create_multiple_course_offerings_active(auth_client.sqla, n)


def test_add_student_to_course_offering(auth_client):
    # Test with incalid student
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(
        url_for('courses.add_student_to_course_offering', person_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test adding an invalid student
    # GIVEN an invalid student
    setup_dependencies_of_student(auth_client, 1)
    person = auth_client.sqla.query(Person).one()
    course_offering = auth_client.sqla.query(Course_Offering).one()
    student = student_object_factory(course_offering.id, person.id)
    del student['confirmed']
    # WHEN requested to create student
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
                                    person_id=person.id), json=student)
    # THEN the response code should be 422
    assert resp.status_code == 422
    # Test adding a valid student
    # GIVEN a course, course offering, and a valid person
    student = student_object_factory(course_offering.id, person.id)
    # WHEN a person wants to enroll in a course offering they become a student
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
                                    person_id=person.id), json=student)
    # THEN the person should be a student in that course
    course_offering = auth_client.sqla.query(Course_Offering).one()
    assert resp.status_code == 201
    assert course_offering.students[0].id == person.id
    # Test adding student already in course
    # GIVEN a valid student that has been added to a course already
    student = student_object_factory(course_offering.id, person.id)
    # WHEN a person tries to register them again
    resp = auth_client.post(url_for('courses.add_student_to_course_offering',
                                    person_id=person.id), json=student)
    # THEN it will throw a 208 error
    assert resp.status_code == 208


def test_read_all_course_offering_students(auth_client):
    # Test with populated database
    # GIVEN existing course offering in database
    count = random.randint(3, 14)
    setup_dependencies_of_student(auth_client, count)
    create_multiple_students(auth_client.sqla, count, 1)
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_all_course_offering_students', course_offering_id=1))
    # THEN assert all entries from database are called
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.smoke
def test_get_all_students(auth_client):
    # GIVEN a set of students
    count = random.randint(3, 6)
    setup_dependencies_of_student(auth_client, count)
    create_multiple_students(auth_client.sqla, count)
    create_multiple_diplomas(auth_client.sqla, count)
    create_diploma_awards(auth_client.sqla, count)

    students = auth_client.sqla.query(Student).all()

    # WHEN all students are requested to be read
    resp = auth_client.get(url_for('courses.get_all_students'))

    # THEN expect the request to run OK
    assert resp.status_code == 200

    # THEN expect the right number of students to come back
    assert len(resp.json) == count

    # THEN expect each student to have the right number of diplomas
    for i in range(count):
        person = auth_client.sqla.query(Person).filter_by(
            id=students[i].student_id).first()
        assert len(resp.json[i]['diplomaList']) == len(person.diplomas_awarded)


def test_read_one_student(auth_client):
    # Test with invalid student
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(url_for('courses.read_one_student', student_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN a student is in the database
    setup_dependencies_of_student(auth_client, 20)
    create_multiple_students(auth_client.sqla, 20)
    create_multiple_diplomas(auth_client.sqla, 20)
    create_diploma_awards(auth_client.sqla, 20)
    # WHEN that student needs to be read
    student = auth_client.sqla.query(Student).first()
    # THEN read that student
    resp = auth_client.get(
        url_for('courses.read_one_student', student_id=student.id))
    assert resp.status_code == 200
    assert resp.json['studentId'] == student.id
    assert resp.json['offeringId'] == student.offering_id
    assert resp.json['confirmed'] == student.confirmed
    assert resp.json['active'] == student.active


def test_update_student(auth_client):
    # Test with valid student
    # GIVEN a student in the database
    setup_dependencies_of_student(auth_client, 1)
    create_multiple_students(auth_client.sqla, 1)
    # WHEN that student needs to be updated
    student = auth_client.sqla.query(Student).one()
    attr = not student.confirmed
    # THEN assert these updates to the student
    resp = auth_client.patch(url_for('courses.update_student', student_id=student.id),
                             json={"offering_id": 1, "student_id": student.id, "confirmed": attr, "active": False})
    assert resp.status_code == 200
    assert resp.json['confirmed'] == attr
    # Test with invalid student
    # GIVEN an invalid student_id
    student_id = 42
    # WHEN the id is updated to student
    resp = auth_client.patch(url_for('courses.update_student', student_id=student_id),
                             json={"offering_id": 1, "student_id": student_id, "confirmed": True, "active": False})
    # THEN there should be a 404 error
    assert resp.status_code == 404


# ---- Class_Attendance


def setup_dependencies_of_class_attendance(auth_client, n):
    setup_dependencies_of_class_meeting(auth_client, 1)
    create_class_meetings(auth_client.sqla, 1)
    create_multiple_students(auth_client.sqla, n)


def test_add_class_attendance(auth_client):
    # Test creating valid class attendance
    # GIVEN course entry to put in database
    count = random.randint(8, 19)
    setup_dependencies_of_class_attendance(auth_client, count)
    students = auth_client.sqla.query(Student).all()
    # WHEN database does not contain entry
    for i in range(len(students) + 1):
        resp = auth_client.post(url_for('courses.add_class_attendance',
                                        course_offering_id=1, class_meeting_id=1), json={'attendance': [i + 1]})
        assert resp.status_code == 200
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(ClassAttendance).count() == len(students)


def test_read_one_class_attendance(auth_client):
    # Test with invalid class offering
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.get(
        url_for('courses.read_one_class_attendance', course_offering_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN course offerings in database
    count = random.randint(3, 15)
    setup_dependencies_of_class_attendance(auth_client, count)
    create_class_attendance(auth_client.sqla, count)
    # WHEN that course offering has attendance
    class_attendance = auth_client.sqla.query(ClassAttendance).first()
    students = auth_client.sqla.query(Student).all()
    # THEN list all prerequisites of given course
    resp = auth_client.get(url_for(
        'courses.read_one_class_attendance', course_offering_id=class_attendance.class_id))
    assert resp.status_code == 200
    for i in range(count):
        assert resp.json[0]['attendance'][i]['studentId'] == students[i].id


def test_read_one_meeting_attendance(auth_client):
    # Test with invalid class meeting
    # GIVEN empty database
    count = random.randint(3, 15)
    setup_dependencies_of_class_meeting(auth_client, 1)
    # WHEN databse queried
    resp = auth_client.get(url_for(
        'courses.read_one_meeting_attendance', course_offering_id=1, class_meeting_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN course offerings in database
    create_class_meetings(auth_client.sqla, 1)
    create_multiple_students(auth_client.sqla, count)
    create_class_attendance(auth_client.sqla, count)
    # WHEN that course offering has attendance
    class_attendance = auth_client.sqla.query(ClassAttendance).first()
    students = auth_client.sqla.query(Student).all()
    # THEN list all prerequisites of given course
    resp = auth_client.get(url_for('courses.read_one_meeting_attendance',
                                   course_offering_id=class_attendance.class_id, class_meeting_id=1))
    assert resp.status_code == 200
    for i in range(count):
        assert resp.json['attendance'][i]['studentId'] == students[i].id


# ---- ClassMeeting


def setup_dependencies_of_class_meeting(auth_client, n):
    Country.load_from_file()
    create_multiple_areas(auth_client.sqla, n)
    create_multiple_addresses(auth_client.sqla, n)
    create_multiple_locations(auth_client.sqla, n)
    create_multiple_people(auth_client.sqla, n)
    create_multiple_courses(auth_client.sqla, n)
    create_multiple_course_offerings(auth_client.sqla, n)


def test_create_class_meeting(auth_client):
    # Test creating invalid class meeting
    # GIVEN invalid class meeting to put in database
    broken_class_meeting = {}
    # WHEN database queried
    resp = auth_client.post(url_for(
        'courses.create_class_meeting', course_offering_id=1), json=broken_class_meeting)
    # THEN assert exception thrown
    assert resp.status_code == 422
    # Test creating valid class meeting
    # GIVEN class meeting to put in database
    setup_dependencies_of_class_meeting(auth_client, 1)
    teacher_id = auth_client.sqla.query(Person).first().id
    offering_id = auth_client.sqla.query(Course_Offering).first().id
    count = random.randint(8, 19)
    # WHEN database does not contain entry
    for i in range(count):
        resp = auth_client.post(url_for('courses.create_class_meeting', course_offering_id=offering_id),
                                json=class_meeting_object_factory(teacher_id, offering_id))
        assert resp.status_code == 201
    # THEN assert that entry is now in database
    assert auth_client.sqla.query(ClassMeeting).count() == count
    # Test creating class meeting that already exists
    duplicate_meeting = class_meeting_object_factory(teacher_id, offering_id)
    resp = auth_client.post(url_for('courses.create_class_meeting',
                                    course_offering_id=offering_id), json=duplicate_meeting)
    resp = auth_client.post(url_for('courses.create_class_meeting',
                                    course_offering_id=offering_id), json=duplicate_meeting)
    assert resp.status_code == 208


def test_read_all_class_meetings(auth_client):
    # GIVEN existing class meetings in database
    setup_dependencies_of_class_meeting(auth_client, 1)
    count = random.randint(3, 11)
    create_class_meetings(auth_client.sqla, count)
    # WHEN call to database
    resp = auth_client.get(
        url_for('courses.read_all_class_meetings', course_offering_id=1))
    # THEN assert all entries from database are called
    assert resp.status_code == 200
    assert len(resp.json) == count


def test_read_one_class_meeting(auth_client):
    # Test with invalid class meeting
    # GIVEN empty database
    # WHEN database queried
    resp = auth_client.get(url_for(
        'courses.read_one_class_meeting', course_offering_id=1, class_meeting_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN one course in the database
    setup_dependencies_of_class_meeting(auth_client, 5)
    count = random.randint(3, 11)
    create_class_meetings(auth_client.sqla, count)
    # WHEN call to database
    meetings = auth_client.sqla.query(ClassMeeting).all()
    # THEN assert entry called is only entry returned
    for meeting in meetings:
        resp = auth_client.get(url_for('courses.read_one_class_meeting',
                                       course_offering_id=meeting.offering_id,
                                       class_meeting_id=meeting.id))
        # THEN we find a matching meeting
        assert resp.status_code == 200
        assert resp.json['offeringId'] == meeting.offering_id
        assert resp.json['teacherId'] == meeting.teacher_id
        assert datetime.strptime(
            resp.json['when'], '%Y-%m-%dT%H:%M:%S+00:00') == meeting.when
        assert resp.json['locationId'] == meeting.location_id


def test_update_class_meeting(auth_client):
    # Test with invalid meeting
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.patch(url_for(
        'courses.update_class_meeting', course_offering_id=1, class_meeting_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN class meeting in database
    setup_dependencies_of_class_meeting(auth_client, 5)
    count = random.randint(3, 11)
    create_class_meetings(auth_client.sqla, count)
    meetings = auth_client.sqla.query(ClassMeeting).all()
    fake = Faker()
    time = str(fake.future_datetime(end_date="+30d"))
    # WHEN course information updated
    for meeting in meetings:
        resp = auth_client.patch(url_for('courses.update_class_meeting',
                                         course_offering_id=meeting.offering_id,
                                         class_meeting_id=meeting.id),
                                 json={'teacherId': 1, 'when': time, 'locationId': 1})
        # THEN assert meeting reflectts new detail(s)
        assert resp.status_code == 200
        assert resp.json['teacherId'] == 1
        assert datetime.strptime(
            resp.json['when'], '%Y-%m-%dT%H:%M:%S+00:00') == datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        assert resp.json['locationId'] == 1
    # Test without fake attribute
    # GIVEN class meeting in database
    # WHEN some fake attribute is to be updated
    resp = auth_client.patch(
        url_for('courses.update_class_meeting', course_offering_id=meeting.offering_id, class_meeting_id=meeting.id),
        json={'fake_attr': 'fake_attr'})
    # THEN assert error code
    assert resp.status_code == 422


def test_delete_class_meeting(auth_client):
    # Test with invalid meeting
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.delete(url_for(
        'courses.delete_class_meeting', course_offering_id=1, class_meeting_id=1))
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN class meeting in database with no attendance
    setup_dependencies_of_class_meeting(auth_client, 1)
    count = random.randint(3, 13)
    create_class_meetings(auth_client.sqla, count)
    meetings = auth_client.sqla.query(ClassMeeting).all()
    # WHEN deleted
    for meeting in meetings:
        resp = auth_client.delete(url_for('courses.delete_class_meeting',
                                          course_offering_id=meeting.offering_id, class_meeting_id=meeting.id))
        count -= 1
        # THEN assert meeting is no longer in database
        assert resp.status_code == 200
        assert auth_client.sqla.query(ClassMeeting).count() == count
    # Test removing attended class
    # GIVEN class meeting that was attended
    create_class_meetings(auth_client.sqla, 1)
    create_multiple_students(auth_client.sqla, 1)
    create_class_attendance(auth_client.sqla, 1)
    meeting = auth_client.sqla.query(ClassMeeting).first()
    # WHEN database queried
    resp = auth_client.delete(url_for('courses.delete_class_meeting',
                                      course_offering_id=meeting.offering_id, class_meeting_id=meeting.id))
    # THEN assert error code
    assert resp.status_code == 403


# ---- Course_Completion
@pytest.mark.xfail()
def test_create_course_completion(auth_client):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


def test_delete_course_completion(auth_client):
    # Test with invalid course completion
    # GIVEN empty database
    # WHEN databse queried
    resp = auth_client.delete(
        url_for('courses.delete_course_completion', courses_id=1), json={'personId': 1})
    # THEN assert error code
    assert resp.status_code == 404
    # Test with populated database
    # GIVEN diploma awarded in database
    create_multiple_people(auth_client.sqla, 1)
    create_multiple_courses(auth_client.sqla, 1)
    course = auth_client.sqla.query(Course).first()
    create_course_completion(auth_client.sqla, 1)
    # WHEN deleted
    resp = auth_client.delete(url_for(
        'courses.delete_course_completion', courses_id=course.id), json={'personId': 1})
    # THEN assert it is gone
    assert resp.status_code == 200
    assert auth_client.sqla.query(CourseCompletion).all() == []


@pytest.mark.smoke
def test_add_course_images(auth_client):
    # GIVEN a set of courses and images
    count = random.randint(3, 6)
    create_multiple_courses(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    courses = auth_client.sqla.query(Course).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN an image is requested to be tied to each course
    for i in range(count):
        print(i)
        resp = auth_client.post(url_for(
            'courses.add_course_images', course_id=courses[i].id, image_id=images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the course to have a single image
        assert len(auth_client.sqla.query(Course).filter_by(
            id=courses[i].id).first().images) == 1


@pytest.mark.smoke
def test_add_course_images_no_exist(auth_client):
    # GIVEN a set of courses and images
    count = random.randint(3, 6)
    create_multiple_courses(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    courses = auth_client.sqla.query(Course).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN a no existant image is requested to be tied to an course
    resp = auth_client.post(
        url_for('courses.add_course_images', course_id=1, image_id=len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existant course
    resp = auth_client.post(
        url_for('courses.add_course_images', course_id=count + 1, image_id=1))

    # THEN expect the course not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_add_course_images_already_exist(auth_client):
    # GIVEN a set of courses, images, and course_image relationships
    count = random.randint(3, 6)
    create_multiple_courses(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_courses(auth_client.sqla)

    course_images = auth_client.sqla.query(ImageCourse).all()

    # WHEN existing course_image relationships are requested to be created
    for course_image in course_images:
        resp = auth_client.post(url_for('courses.add_course_images',
                                        course_id=course_image.course_id,
                                        image_id=course_image.image_id))

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_course_image(auth_client):
    # GIVEN a set of courses, images, and course_image relationships
    count = random.randint(3, 6)
    create_multiple_courses(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_courses(auth_client.sqla)

    valid_course_image = auth_client.sqla.query(ImageCourse).first()

    # WHEN the course_image relationships are requested to be deleted
    resp = auth_client.delete(url_for('courses.delete_course_image',
                                      course_id=valid_course_image.course_id,
                                      image_id=valid_course_image.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204


@pytest.mark.smoke
def test_delete_course_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a course_image relationship is requested to be deleted
    resp = auth_client.delete(url_for('courses.delete_course_image',
                                      course_id=random.randint(1, 8),
                                      image_id=random.randint(1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404

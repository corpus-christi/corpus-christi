from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import (
    Course, CourseCreate, CourseUpdate, CourseSchema,
    Course_Offering, CourseOfferingCreate, CourseOfferingSchema,
    Diploma, DiplomaCreate, DiplomaUpdate, DiplomaSchema,
    DiplomaAwarded, DiplomaAwardedCreate, DiplomaAwardedSchema,
    Student, StudentCreate, StudentSchema,
    ClassMeeting, ClassMeetingCreate, ClassMeetingSchema,
    ClassAttendance, ClassAttendanceSchema,
    CourseCompletion, CourseCompletionSchema,
    DiplomaCourse,
)
from ..images.models import Image, ImageCourse
from ..people.models import Person, PersonSchema
from ..places.models import LocationSchema

router = APIRouter()

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


# ---- Helpers

def add_prereqs(db: Session, query_result):
    if hasattr(query_result, '__iter__') and not hasattr(query_result, 'id'):
        courses_list = course_schema.dump(query_result, many=True)
        for i in range(len(courses_list)):
            courses_list[i]['prerequisites'] = []
            for j in query_result[i].prerequisites:
                j_dumped = course_schema.dump(j, many=False)
                j_dumped.pop('diplomaList', None)
                courses_list[i]['prerequisites'].append(j_dumped)
        return courses_list
    else:
        course_dict = course_schema.dump(query_result, many=False)
        course_dict['prerequisites'] = []
        for i in query_result.prerequisites:
            course_dict['prerequisites'].append(course_schema.dump(i, many=False))
        return course_dict


def include_course_offerings(db: Session, course: dict) -> dict:
    course['course_offerings'] = []
    offerings = db.execute(select(Course_Offering).where(Course_Offering.course_id == course['id'])).scalars().all()
    for i in offerings:
        course['course_offerings'].append(course_offering_schema.dump(i))
    return course


# ---- Courses

@router.post("/courses", status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_course = Course(**course_schema.load(payload.model_dump()))
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return course_schema.dump(new_course)


@router.get("/courses")
def read_all_courses(db: Session = Depends(get_db)):
    result = db.execute(select(Course)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="Result NOT found")
    for course in result:
        course.diplomaList = course.diplomas
    result_list = list(result)
    with_prereqs = add_prereqs(db, result_list)
    for i in with_prereqs:
        include_course_offerings(db, i)
    return with_prereqs


@router.get("/{active_state}/courses")
def read_active_state_of_courses(active_state: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if active_state == 'active':
        result = db.execute(select(Course).where(Course.active == True)).scalars().all()
    elif active_state == 'inactive':
        result = db.execute(select(Course).where(Course.active == False)).scalars().all()
    else:
        raise HTTPException(status_code=404, detail="Result NOT found")
    return course_schema.dump(result, many=True)


@router.get("/courses/{course_id}")
def read_one_course(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.get(Course, course_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result NOT found")
    with_prereqs = add_prereqs(db, result)
    with_offerings = include_course_offerings(db, with_prereqs)
    return with_offerings


@router.patch("/courses/{course_id}")
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Not Found")
    for attr in ("description", "active", "name"):
        val = getattr(payload, attr, None)
        if val is not None:
            setattr(course, attr, val)
    db.commit()
    return course_schema.dump(course)


# ---- Prerequisite

@router.post("/courses/{course_id}/prerequisites", status_code=201)
def create_prerequisite(course_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course to add prereqs not found")
    for p in payload.get('prerequisites', []):
        if p == course.id:
            continue
        prereq = db.get(Course, p)
        if prereq:
            course.prerequisites.append(prereq)
    db.commit()
    return course_schema.dump(course)


@router.get("/courses/prerequisites")
def read_all_prerequisites(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Course)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No courses found")
    results = []
    for i in result:
        for j in i.prerequisites:
            results.append(j)
    return course_schema.dump(results, many=True)


@router.get("/courses/{course_id}/prerequisites")
def read_one_course_prerequisites(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.get(Course, course_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course_schema.dump(result.prerequisites, many=True)


@router.patch("/courses/{course_id}/prerequisites")
def update_prerequisite(course_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course to update prereqs not found")
    prereq_ids = payload.get('prerequisites', [])
    for i in list(course.prerequisites):
        if i.id not in prereq_ids:
            course.prerequisites.remove(i)
    for i in prereq_ids:
        if i == course.id:
            continue
        prereq = db.get(Course, i)
        if prereq and prereq not in course.prerequisites:
            course.prerequisites.append(prereq)
    db.commit()
    return course_schema.dump(course)


# ---- Course_Offering

@router.post("/course_offerings", status_code=201)
def create_course_offering(payload: CourseOfferingCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_co = Course_Offering(**course_offering_schema.load(payload.model_dump()))
    db.add(new_co)
    db.commit()
    db.refresh(new_co)
    return course_offering_schema.dump(new_co)


@router.get("/course_offerings")
def read_all_course_offerings(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Course_Offering)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No Course Offerings found")
    results = course_offering_schema.dump(result, many=True)
    for r in results:
        course = db.get(Course, r['courseId'])
        r['course'] = course_schema.dump(course) if course else {}
    return results


@router.get("/course_offerings/{course_offering_id}")
def read_one_course_offering(course_offering_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    co = db.get(Course_Offering, course_offering_id)
    if co is None:
        raise HTTPException(status_code=404, detail="Course Offering not found")
    result = course_offering_schema.dump(co)
    course = db.get(Course, result['courseId'])
    result['course'] = course_schema.dump(course) if course else {}
    return result


@router.get("/{active_state}/course_offerings")
def read_active_state_course_offerings(active_state: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if active_state == 'active':
        query = db.execute(select(Course_Offering).where(Course_Offering.active == True)).scalars().all()
    elif active_state == 'inactive':
        query = db.execute(select(Course_Offering).where(Course_Offering.active == False)).scalars().all()
    else:
        raise HTTPException(status_code=404, detail="Cannot filter course offerings with undefined state")
    return course_offering_schema.dump(query, many=True)


@router.patch("/course_offerings/{course_offering_id}")
def update_course_offering(course_offering_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    co = db.get(Course_Offering, course_offering_id)
    if co is None:
        raise HTTPException(status_code=404, detail="Course Offering NOT Found")
    valid_co = course_offering_schema.load(payload, partial=True)
    for attr, val in valid_co.items():
        setattr(co, attr, val)
    db.commit()
    return course_offering_schema.dump(co)


# ---- Diploma

@router.post("/diplomas", status_code=201)
def create_diploma(payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    course_list = payload.pop('courseList', [])
    new_diploma = Diploma(**diploma_schema.load(payload))
    for course_id in course_list:
        course = db.get(Course, course_id)
        if course:
            new_diploma.courses.append(course)
    db.add(new_diploma)
    db.commit()
    db.refresh(new_diploma)
    new_diploma.courseList = new_diploma.courses
    return diploma_schema.dump(new_diploma)


@router.get("/diplomas")
def read_all_diplomas(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(Diploma)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No Diplomas found")
    for diploma in result:
        diploma.courseList = diploma.courses
        students = []
        for da in diploma.diplomas_awarded:
            students.append(da.students)
        diploma.studentList = students
    return diploma_schema.dump(result, many=True)


@router.get("/diplomas/{diploma_id}")
def read_one_diploma(diploma_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.get(Diploma, diploma_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Diploma not found")
    result.courseList = result.courses
    students = []
    for da in result.diplomas_awarded:
        students.append(da.students)
    result.studentList = students
    return diploma_schema.dump(result)


@router.patch("/diplomas/{diploma_id}")
def update_diploma(diploma_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma = db.get(Diploma, diploma_id)
    if diploma is None:
        raise HTTPException(status_code=404, detail=f"Diploma with id #{diploma_id} not found")
    course_list = payload.pop('courseList', None)
    valid_diploma = diploma_schema.load(payload, partial=True)
    for key, val in valid_diploma.items():
        setattr(diploma, key, val)
    if course_list is not None:
        diploma.courses = []
        for cid in course_list:
            course = db.get(Course, cid)
            if course:
                diploma.courses.append(course)
    db.commit()
    diploma.courseList = diploma.courses
    return diploma_schema.dump(diploma)


@router.put("/diplomas/{diploma_id}/{course_id}")
def add_course_to_diploma(diploma_id: int, course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma = db.get(Diploma, diploma_id)
    course = db.get(Course, course_id)
    if course not in diploma.courses:
        diploma.courses.append(course)
    else:
        raise HTTPException(status_code=409, detail='Course already in diploma')
    db.commit()
    diploma.courseList = diploma.courses
    return diploma_schema.dump(diploma)


@router.delete("/diplomas/{diploma_id}/{course_id}")
def remove_course_from_diploma(diploma_id: int, course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma = db.get(Diploma, diploma_id)
    course = db.get(Course, course_id)
    if course in diploma.courses:
        if diploma.diplomas_awarded:
            raise HTTPException(status_code=403, detail=f"Student was awarded diploma #{diploma.id}")
        diploma.courses.remove(course)
    else:
        raise HTTPException(status_code=404, detail=f"Course #{course_id} not associated with diploma #{diploma_id}")
    db.commit()
    diploma.courseList = diploma.courses
    return 'Successfully deleted course association with diploma'


@router.patch("/diplomas/activate/{diploma_id}")
def activate_diploma(diploma_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma = db.get(Diploma, diploma_id)
    if diploma is None:
        raise HTTPException(status_code=404, detail="Not Found")
    setattr(diploma, 'active', True)
    db.commit()
    return diploma_schema.dump(diploma)


@router.patch("/diplomas/deactivate/{diploma_id}")
def deactivate_diploma(diploma_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma = db.get(Diploma, diploma_id)
    if diploma is None:
        raise HTTPException(status_code=404, detail="Not Found")
    setattr(diploma, 'active', False)
    db.commit()
    return diploma_schema.dump(diploma)


# ---- DiplomaAwarded

@router.post("/diplomas_awarded", status_code=201)
def create_diploma_awarded(payload: DiplomaAwardedCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valid = diploma_awarded_schema.load(payload.model_dump())
    existing = db.execute(
        select(DiplomaAwarded).where(
            DiplomaAwarded.person_id == valid['person_id'],
            DiplomaAwarded.diploma_id == valid['diploma_id']
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail=f"Diploma #{valid['diploma_id']} already awarded to person #{valid['person_id']}")
    new_da = DiplomaAwarded(**valid)
    db.add(new_da)
    db.commit()
    return diploma_awarded_schema.dump(new_da)


@router.get("/diplomas_awarded")
def read_all_diplomas_awarded(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(DiplomaAwarded)).scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="No Diplomas Awarded found")
    return diploma_awarded_schema.dump(result, many=True)


@router.get("/diplomas_awarded/{person_id}/{diploma_id}")
def read_one_diploma_awarded(person_id: int, diploma_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(
        select(DiplomaAwarded).where(DiplomaAwarded.person_id == person_id, DiplomaAwarded.diploma_id == diploma_id)
    ).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Diploma for person #{person_id} and diploma #{diploma_id} not found")
    return diploma_awarded_schema.dump(result)


@router.get("/diplomas_awarded/{diploma_id}/students")
def read_all_students_diploma_awarded(diploma_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(
        select(Diploma, DiplomaAwarded, Person)
        .where(Diploma.id == diploma_id)
        .join(DiplomaAwarded, DiplomaAwarded.diploma_id == Diploma.id)
        .join(Person, Person.id == DiplomaAwarded.person_id)
    ).all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No results for diploma with id #{diploma_id} found")
    diploma = diploma_schema.dump(rows[0][0])
    diploma['students'] = []
    for row in rows:
        p = person_schema.dump(row[2])
        p['diplomaAwarded'] = diploma_awarded_schema.dump(row[1])['when']
        diploma['students'].append(p)
    return diploma


@router.patch("/diplomas_awarded/{diploma_id}/{person_id}")
def update_diploma_awarded(diploma_id: int, person_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma_awarded = db.execute(
        select(DiplomaAwarded).where(DiplomaAwarded.diploma_id == diploma_id, DiplomaAwarded.person_id == person_id)
    ).scalar_one_or_none()
    if diploma_awarded is None:
        raise HTTPException(status_code=404, detail=f"Diploma with id {diploma_id} not found")
    if 'when' in payload:
        setattr(diploma_awarded, 'when', payload['when'])
    db.commit()
    return diploma_awarded_schema.dump(diploma_awarded)


@router.delete("/diplomas_awarded/{diploma_id}/{person_id}")
def delete_diploma_awarded(diploma_id: int, person_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    diploma_awarded = db.execute(
        select(DiplomaAwarded).where(DiplomaAwarded.diploma_id == diploma_id, DiplomaAwarded.person_id == person_id)
    ).scalar_one_or_none()
    if diploma_awarded is None:
        raise HTTPException(status_code=404, detail=f"That diploma #{diploma_id} for student #{person_id} does not exist")
    db.delete(diploma_awarded)
    db.commit()
    return diploma_awarded_schema.dump(diploma_awarded)


# ---- Student

@router.post("/course_offerings/{person_id}", status_code=201)
def add_student_to_course_offering(person_id: int, payload: StudentCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person NOT in database")
    valid_student = student_schema.load(payload.model_dump())
    course_offering = payload.offeringId
    student_in_co = db.execute(
        select(Student).where(Student.student_id == person_id, Student.offering_id == course_offering)
    ).scalar_one_or_none()
    if student_in_co is None:
        new_student = Student(**valid_student)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        to_return = student_schema.dump(new_student)
        to_return['person'] = person_schema.dump(person)
        return to_return
    else:
        raise HTTPException(status_code=208, detail="Student already enrolled in course offering")


@router.get("/course_offerings/{course_offering_id}/students")
def read_all_course_offering_students(course_offering_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    co = db.get(Course_Offering, course_offering_id)
    if co is None:
        raise HTTPException(status_code=404, detail="Course Offering NOT found")
    rows = db.execute(
        select(Student, Person)
        .where(Student.offering_id == course_offering_id)
        .join(Person, Person.id == Student.student_id)
    ).all()
    student_list = []
    for row in rows:
        s = student_schema.dump(row[0])
        s['person'] = person_schema.dump(row[1])
        student_list.append(s)
    return student_list


@router.get("/students")
def get_all_students(db: Session = Depends(get_db), _=Depends(get_current_user)):
    people = db.execute(select(Person).join(Student, Student.student_id == Person.id)).scalars().all()
    to_return = []
    for person in people:
        p = person_schema.dump(person)
        p['diplomaList'] = []
        for da in person.diplomas_awarded:
            d = db.get(Diploma, da.diploma_id)
            if d:
                d_dumped = diploma_schema.dump(d)
                d_dumped['diplomaIsActive'] = d_dumped.pop('active')
                p['diplomaList'].append(d_dumped)
        to_return.append(p)
    return to_return


@router.get("/students/{student_id}")
def read_one_student(student_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(
        select(Student, Person, Course_Offering, Course)
        .where(Student.student_id == student_id)
        .join(Person, Person.id == Student.student_id)
        .join(Course_Offering, Course_Offering.id == Student.offering_id)
        .join(Course, Course.id == Course_Offering.course_id)
    ).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Student not found")

    diplomas = []
    for da in rows[0][1].diplomas_awarded:
        diplomas.append(da.diplomas)
    rows[0][0].diplomaList = diplomas

    r = student_schema.dump(rows[0][0])
    r['person'] = person_schema.dump(rows[0][1])
    r['courses'] = []
    r['diplomaList'] = []

    for da in rows[0][1].diplomas_awarded:
        d = db.get(Diploma, da.diploma_id)
        d_dumped = diploma_schema.dump(d) if d else {}
        d_dumped['diplomaIsActive'] = d_dumped.pop('active', None)
        award = db.execute(
            select(DiplomaAwarded).where(
                DiplomaAwarded.person_id == r['person']['id'],
                DiplomaAwarded.diploma_id == da.diploma_id
            )
        ).scalar_one_or_none()
        d_dumped['when'] = diploma_awarded_schema.dump(award)['when'] if award else None
        r['diplomaList'].append(d_dumped)

    for diploma in r['diplomaList']:
        diploma_courses = db.execute(
            select(DiplomaCourse).where(DiplomaCourse.c.diploma_id == diploma['id'])
        ).all()
        diploma['courses'] = []
        for dc in diploma_courses:
            cq = db.get(Course, dc.course_id)
            if cq:
                cq_dumped = course_schema.dump(cq)
                cq_dumped['id'] = dc.course_id
                cq_dumped.pop('description', None)
                cq_dumped.pop('active', None)
                diploma['courses'].append(cq_dumped)
        for course in diploma['courses']:
            completion = db.execute(
                select(CourseCompletion).where(
                    CourseCompletion.course_id == course['id'],
                    CourseCompletion.person_id == r['person']['id']
                )
            ).scalar_one_or_none()
            course['courseCompleted'] = completion is not None

    for row in rows:
        r['courses'].append(course_schema.dump(row[3]))
    for i in r['courses']:
        i['courseOfferings'] = []
        completion = db.execute(
            select(CourseCompletion).where(
                CourseCompletion.course_id == i['id'],
                CourseCompletion.person_id == r['person']['id']
            )
        ).scalar_one_or_none()
        i['courseCompleted'] = completion is not None
        for row in rows:
            if row[2].course_id == i['id']:
                co = course_offering_schema.dump(row[2])
                co['courseIsActive'] = i['active']
                co['courseOfferingIsActive'] = co.pop('active')
                co.pop('id', None)
                co.pop('courseId', None)
                i['courseOfferings'].append(co)
    return r


@router.patch("/students/{student_id}")
def update_student(student_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    for attr in ('confirmed', 'active'):
        if attr in payload:
            setattr(student, attr, payload[attr])
    db.commit()
    return student_schema.dump(student)


# ---- Course_Completion

@router.post("/courses/{courses_id}/course_completion", status_code=201)
def create_course_completion(courses_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    person_id = payload.get('personId')
    person_enrolled = db.execute(
        select(Person, Student, Course_Offering, Course)
        .where(Person.id == person_id)
        .join(Student, Student.student_id == Person.id)
        .join(Course_Offering, Course_Offering.id == Student.offering_id)
        .where(Course_Offering.course_id == courses_id)
        .join(Course, Course.id == Course_Offering.course_id)
    ).first()
    if person_enrolled is None:
        raise HTTPException(status_code=404, detail=f"Person #{person_id} is not enrolled in any course offerings with course #{courses_id}.")

    person_completed = db.execute(
        select(CourseCompletion).where(CourseCompletion.course_id == courses_id, CourseCompletion.person_id == person_id)
    ).scalar_one_or_none()
    if person_completed:
        raise HTTPException(status_code=403, detail=f"Entry for Person #{person_id} with completed course #{courses_id} already exists.")

    new_cc = CourseCompletion(person_id=person_id, course_id=courses_id)
    db.add(new_cc)
    db.commit()
    return f"Person #{person_id} has successfully completed course #{courses_id}."


@router.delete("/courses/{courses_id}/course_completion")
def delete_course_completion(courses_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    person_id = payload.get('personId')
    cc = db.execute(
        select(CourseCompletion).where(CourseCompletion.course_id == courses_id, CourseCompletion.person_id == person_id)
    ).scalar_one_or_none()
    if cc is not None:
        db.delete(cc)
        db.commit()
        return 'Course completion successfully deleted'
    else:
        raise HTTPException(status_code=404, detail=f"Cannot remove non-existing entry. Person #{person_id} with completed course #{courses_id} DNE.")


# ---- ClassMeeting

@router.post("/course_offerings/{course_offering_id}/class_meetings", status_code=201)
def create_class_meeting(course_offering_id: int, payload: ClassMeetingCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valid_cm = class_meeting_schema.load(payload.model_dump())
    existing = db.execute(
        select(ClassMeeting).where(
            ClassMeeting.offering_id == course_offering_id,
            ClassMeeting.teacher_id == valid_cm['teacher_id'],
            ClassMeeting.when == valid_cm['when']
        )
    ).scalar_one_or_none()
    if existing is None:
        new_cm = ClassMeeting(**valid_cm)
        db.add(new_cm)
        db.commit()
        db.refresh(new_cm)
        return class_meeting_schema.dump(new_cm)
    else:
        raise HTTPException(status_code=208, detail="Class meeting already exists in course offering")


@router.get("/course_offerings/{course_offering_id}/class_meetings")
def read_all_class_meetings(course_offering_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(select(ClassMeeting).where(ClassMeeting.offering_id == course_offering_id)).scalars().all()
    return class_meeting_schema.dump(result, many=True)


@router.get("/course_offerings/{course_offering_id}/{class_meeting_id}")
def read_one_class_meeting(course_offering_id: int, class_meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = db.execute(
        select(ClassMeeting).where(ClassMeeting.id == class_meeting_id, ClassMeeting.offering_id == course_offering_id)
    ).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Specified class meeting does not exist for this course offering")
    return class_meeting_schema.dump(result)


@router.patch("/course_offerings/{course_offering_id}/{class_meeting_id}")
def update_class_meeting(course_offering_id: int, class_meeting_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    cm = db.execute(
        select(ClassMeeting).where(ClassMeeting.id == class_meeting_id, ClassMeeting.offering_id == course_offering_id)
    ).scalar_one_or_none()
    if cm is None:
        raise HTTPException(status_code=404, detail="Class meeting not found")
    valid_cm = class_meeting_schema.load(payload, partial=True)
    for key, val in valid_cm.items():
        setattr(cm, key, val)
    db.commit()
    return class_meeting_schema.dump(cm)


@router.delete("/course_offerings/{course_offering_id}/{class_meeting_id}")
def delete_class_meeting(course_offering_id: int, class_meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    cm = db.execute(
        select(ClassMeeting).where(ClassMeeting.id == class_meeting_id, ClassMeeting.offering_id == course_offering_id)
    ).scalar_one_or_none()
    attended = db.execute(
        select(ClassAttendance).where(ClassAttendance.c.class_id == class_meeting_id)
    ).first()
    if cm is not None and attended is None:
        db.delete(cm)
        db.commit()
        return 'Class meeting successfully deleted'
    elif cm is None:
        raise HTTPException(status_code=404, detail="Course offering does not exist")
    else:
        raise HTTPException(status_code=403, detail="Students have attended the class meeting. Cannot delete class meeting.")


# ---- Class_Attendance

def _add_attendance_to_meetings(db: Session, json_meeting: dict) -> dict:
    json_meeting['attendance'] = []
    rows = db.execute(
        select(ClassAttendance, Student, Person)
        .where(ClassAttendance.c.class_id == json_meeting['id'])
        .join(Student, Student.id == ClassAttendance.c.student_id)
        .join(Person, Person.id == Student.student_id)
    ).all()
    for row in rows:
        ca, student, person = row[0], row[1], row[2]
        json_meeting['attendance'].append({
            "classId": ca.class_id,
            "studentId": ca.student_id,
            "name": person.full_name()
        })
    return json_meeting


@router.post("/course_offerings/{course_offering_id}/{class_meeting_id}/class_attendance")
def add_class_attendance(course_offering_id: int, class_meeting_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    cm = db.get(ClassMeeting, class_meeting_id)
    if cm is None:
        raise HTTPException(status_code=404, detail="Class Meeting not found")
    new_attendance = []
    for student_id in payload.get('attendance', []):
        student = db.execute(
            select(Student).where(Student.id == student_id, Student.offering_id == course_offering_id)
        ).scalar_one_or_none()
        if student is None:
            continue
        student.attendance.append(cm)
        new_attendance.append(student)
    db.add_all(new_attendance)
    db.commit()
    return _add_attendance_to_meetings(db, class_meeting_schema.dump(cm))


@router.get("/course_offerings/{course_offering_id}/class_attendance")
def read_one_class_attendance(course_offering_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meetings = db.execute(select(ClassMeeting).where(ClassMeeting.offering_id == course_offering_id)).scalars().all()
    if not meetings:
        raise HTTPException(status_code=404, detail="Class Meetings NOT found for this course offering")
    result = class_meeting_schema.dump(meetings, many=True)
    for m in result:
        _add_attendance_to_meetings(db, m)
    return result


@router.get("/course_offerings/{course_offering_id}/{class_meeting_id}/class_attendance")
def read_one_meeting_attendance(course_offering_id: int, class_meeting_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    meeting = db.execute(
        select(ClassMeeting).where(ClassMeeting.offering_id == course_offering_id, ClassMeeting.id == class_meeting_id)
    ).scalar_one_or_none()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Class Meeting NOT found")
    m = class_meeting_schema.dump(meeting)
    _add_attendance_to_meetings(db, m)
    return m


@router.patch("/course_offerings/{course_offering_id}/{class_meeting_id}/class_attendance")
def update_class_attendance(course_offering_id: int, class_meeting_id: int, payload: dict = Body(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    current_attendance = db.execute(
        select(ClassAttendance).where(ClassAttendance.c.class_id == class_meeting_id)
    ).all()
    current_list = [{"classId": r.class_id, "studentId": r.student_id} for r in current_attendance]
    cm = db.get(ClassMeeting, class_meeting_id)
    updated_list = [{"classId": class_meeting_id, "studentId": i} for i in payload.get('attendance', [])]
    updates = []
    for item in current_list:
        if item not in updated_list:
            student = db.execute(
                select(Student).where(Student.id == item['studentId'], Student.offering_id == course_offering_id)
            ).scalar_one_or_none()
            if student is None:
                continue
            student.attendance.remove(cm)
            updates.append(student)
    for item in updated_list:
        if item not in current_list:
            student = db.execute(
                select(Student).where(Student.id == item['studentId'], Student.offering_id == course_offering_id)
            ).scalar_one_or_none()
            if student is None:
                continue
            student.attendance.append(cm)
            updates.append(student)
    db.add_all(updates)
    db.commit()
    return _add_attendance_to_meetings(db, class_meeting_schema.dump(cm))


# ---- Image

@router.post("/{course_id}/images/{image_id}", status_code=201)
def add_course_images(course_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id #{course_id} does not exist.")
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")
    course_image = db.execute(
        select(ImageCourse).where(ImageCourse.course_id == course_id, ImageCourse.image_id == image_id)
    ).scalar_one_or_none()
    if course_image:
        raise HTTPException(status_code=422, detail=f"Image with id#{image_id} is already attached to course with id#{course_id}.")
    new_entry = ImageCourse(course_id=course_id, image_id=image_id)
    db.add(new_entry)
    db.commit()
    return f"Image with id #{image_id} successfully added to Course with id #{course_id}."


@router.put("/{course_id}/images/{image_id}")
def put_course_images(course_id: int, image_id: int, old: Optional[str] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    new_image_id = image_id
    if old == 'false' or old is None:
        add_course_images(course_id, new_image_id, db)
        return {'deleted': 'No image to delete', 'posted': f"Image with id #{new_image_id} successfully added to Course with id #{course_id}."}
    else:
        old_image_id = int(old)
        old_img = db.execute(
            select(ImageCourse).where(ImageCourse.course_id == course_id, ImageCourse.image_id == old_image_id)
        ).scalar_one_or_none()
        deleted_msg = 'Not found'
        if old_img:
            db.delete(old_img)
            deleted_msg = 'Successfully removed image'
        add_course_images(course_id, new_image_id, db)
        return {'deleted': deleted_msg, 'posted': f"Image with id #{new_image_id} successfully added to Course with id #{course_id}."}


@router.delete("/{course_id}/images/{image_id}", status_code=204)
def delete_course_image(course_id: int, image_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    course_image = db.execute(
        select(ImageCourse).where(ImageCourse.course_id == course_id, ImageCourse.image_id == image_id)
    ).scalar_one_or_none()
    if not course_image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} is not assigned to Course with id #{course_id}.")
    db.delete(course_image)
    db.commit()

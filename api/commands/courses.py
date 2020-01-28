import click
from flask.cli import AppGroup
from src import db
from src.courses.models import Course, Course_Offering, Diploma


def create_course_cli(app):
    course_cli = AppGroup('courses', help="Maintain course data.")

    @course_cli.command('create-course', help="Create new course")
    @click.argument('name')
    @click.argument('description')
    @click.option('--prereq', help="Name of prerequisite")
    @click.option('--offering', help="Name of offering to make for course")
    def create_course(name, description, prereq, offering):
        # Create the Course and Prereq Courses; commit to DB so we get ID
        course = Course(name=name, description=description)

        if prereq is not None:
            prereq_course = db.session.query(
                Course).filter_by(name=prereq).first()
            print(prereq_course)
            course.prerequisites.append(prereq_course)

        if offering is not None:
            course_offering = Course_Offering(course_id=course.id,
                                              description=offering, max_size=2, active=True)
            course.courses_offered.append(course_offering)
        db.session.add(course)
        db.session.commit()
        print(f"Created {course}")
        print(f"Created Prerequisites {course.prerequisites}")
        print(f"Created Course Offering {course.courses_offered}")

    @course_cli.command('create-diploma', help="Create new diploma")
    @click.argument('name')
    @click.argument('description')
    def create_diploma(name, description):
        # Create the diploma; commit to DB so we get ID
        diploma = Diploma(name=name, description=description)
        db.session.add(diploma)
        db.session.commit()
        print(f"Created Diploma {diploma}")

    app.cli.add_command(course_cli)

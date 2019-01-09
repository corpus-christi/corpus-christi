import pytest
# ---- Course

# Test course creation
@pytest.mark.xfail()
def test_create_course(client, db):
    # GIVEN course entry to put in database
    # WHEN database does not contain entry
    # THEN assert that entry is now in database
    assert True == False
    
# Test getting all courses from the database
@pytest.mark.xfail()
def test_read_all_courses(client, db):
    # GIVEN many courses in database
    # WHEN call to database
    # THEN assert all entries from database are called
    assert True == False
    
# Test reading a single course from the database
@pytest.mark.xfail()
def test_read_one_course(client, db):
    # GIVEN one course in the database
    # WHEN call to database
    # THEN assert entry called is only entry returned 
    assert True == False


@pytest.mark.xfail()
def test_deactivate_course(client, db):
    # GIVEN course to deactivate
    # WHEN course is deactivated
    # THEN assert course is no longer active
    assert True == False

@pytest.mark.xfail()
def test_reactivate_course(client, db):
    # GIVEN deactivated course
    # WHEN course is reactivated
    # THEN assert course is active
    assert True == False

""" 
# Test 
@pytest.mark.xfail()
def test_replace_course(client, db):
    # GIVEN a deactivated course in database
    # WHEN 
    # THEN assert
    assert True == False
"""

@pytest.mark.xfail()
def test_update_course(client, db):
    # GIVEN outdated course in database
    # WHEN course information updated
    # THEN assert course reflects new details
    assert True == False
    

@pytest.mark.xfail()
def test_delete_course(client, db):
    # GIVEN undesirable course in database
    # WHEN course is removed
    # THEN assert course and all associated information deleted
    assert True == False
    

# ---- Prerequisite


@pytest.mark.xfail()
def test_create_prerequisite(client, db):
    # GIVEN existing and available course in database
    # WHEN course requires previous attendance to another course
    # THEN add course as prerequisite
    assert True == False
    
# This will test getting all prerequisites for a single course
@pytest.mark.xfail()
def test_read_all_prerequisites(client, db):
    # GIVEN existing and available course in database
    # WHEN that course has prerequisites
    # THEN assert all prereq's are listed
    assert True == False

#FIX NAME (Will test to see all courses that have given course as a prerequisite)
def test_read_all_courses_with_prerequisite(client, db):
    #GIVEN prerequisite course in database
    #WHEN other courses have that course as a prerequisite
    #THEN list all courses with given prerequisite
    assert True == False


#PROBABLY DON'T NEED THESE TWO
# @pytest.mark.xfail()
# def test_read_one_prerequisite(client, db):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False
    

# @pytest.mark.xfail()
# def test_replace_prerequisite(client, db):
#     # GIVEN
#     # WHEN
#     # THEN
#     assert True == False
    

@pytest.mark.xfail()
def test_update_prerequisite(client, db):
    # GIVEN 
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_prerequisite(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

# ---- Course_Offering


@pytest.mark.xfail()
def test_create_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_all_course_offerings(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_read_one_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_replace_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_update_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

@pytest.mark.xfail()
def test_delete_course_offering(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    

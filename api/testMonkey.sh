#!/usr/bin/env bash

#pytest -x src/people/test_people.py
#pytest src/people/test_people.py::test_activate_person_no_exist
#pytest src/people/test_people.py::test_read_one_account
#pytest src/people/test_people.py::test_create_account
pytest src/people/test_people.py --cov=src --cov-report=html



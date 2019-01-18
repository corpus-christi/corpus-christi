#!/usr/bin/env bash

#pytest -x src/people/test_people.py
#pytest src/people/test_people.py::test_get_accounts_by_role
#pytest src/people/test_people.py::test_read_one_account
pytest src/people/test_people.py --cov=src --cov-report=html

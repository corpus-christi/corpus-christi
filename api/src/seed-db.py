"""
Seed the database.

This is a `pytest` file that leverages the data fixtures we've created
in the test modules to put some plausible data in the database.

As additional test modules are created, define a `seed_database`
function in each and import and invoke it here.

In order to avoid running this during normal testing, it's stored in a file that
is not discovered by `pytest`. To run it, do something like

   FLASK_CONFIG=dev pytest src/seed-db.py
"""
from src.i18n.test_i18n import seed_database


def test_seed_database(dbs):
    seed_database(dbs)

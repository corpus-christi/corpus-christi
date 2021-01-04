from flask.cli import AppGroup

from api.src import db
from api.src.groups.create_group_data import (
    create_hierarchy_test_case_1,
    create_hierarchy_test_case_2,
    create_multiple_group_types,
    create_multiple_manager_types)


def create_group_cli(app):
    group_cli = AppGroup('groups', help="Group-related cli.")
    app.cli.add_command(group_cli)

    @group_cli.command('hierarchy-test-1', short_help='Generate group hierarchy test data')
    def generate_hierarchy_test_1_data():
        """ 
        This test case contains a typical hierarchical leadership structure.

        Once the test data is generated, one should be able to view the
        leadership hierarchy under the UI's treeview page.
        """
        create_multiple_group_types(db.session, 5)
        create_multiple_manager_types(db.session, 5)
        create_hierarchy_test_case_1(db.session)

    @group_cli.command('hierarchy-test-2', short_help='Generate group hierarchy test data')
    def generate_hierarchy_test_2_data():
        """ 
        This test case contains an invalid hierarchical leadership strcture
        that contains a cycle.

        Once the test data is generated, one should see a warning under the
        UI's treeview page.
        """
        create_multiple_group_types(db.session, 5)
        create_multiple_manager_types(db.session, 5)
        create_hierarchy_test_case_2(db.session)

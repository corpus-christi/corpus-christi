import click
from click import BadParameter
from flask.cli import AppGroup

from .. import db
from ..people.models import Person, Role


def create_account_cli(app):
    user_cli = AppGroup('people', help="Maintain accounts.")

    @user_cli.command('new', help="Create new person")
    @click.argument('username')
    @click.argument('password')
    @click.option('--first', help="First name")
    @click.option('--last', help="Last name")
    @click.option('--email', help="Email address")
    @click.option(
        '--roles',
        help="Attach roles to the person",
        multiple=True,
        default=['role.public'])
    def create_account(username, password, first, last, email, roles):
        first_name = first or 'Test'
        last_name = last or 'User'

        # Make sure no existing user.
        person = db.session.query(Person).filter_by(username=username).first()
        if person is not None:
            raise BadParameter(
                f"Already an account with username '{username}'")

        fetched_roles = []
        for role_name in roles:
            role = db.session.query(Role).filter_by(
                name_i18n=role_name).first()
            if role:
                print(f"Attaching role {role_name} to person")
                fetched_roles.append(role)
            else:
                print(
                    f"Role {role_name} not found in database, not attached to person")

        # Create the Person; commit to DB so we get ID
        person = Person(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            email=email,
            roles=fetched_roles)
        db.session.add(person)
        db.session.commit()
        print(f"Created {person}")

    @user_cli.command('password', help="Change password")
    @click.argument('username')
    @click.argument('password')
    def update_password(username, password):
        person = db.session.query(Person).filter_by(username=username).first()
        if person is None:
            raise BadParameter(f"No account with username '{username}'")

        person.password = password
        db.session.commit()
        print(f"Password for '{username}' updated")

    app.cli.add_command(user_cli)

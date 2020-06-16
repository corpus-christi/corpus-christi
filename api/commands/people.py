import click
from click import BadParameter
from flask.cli import AppGroup
from src import db
from src.people.models import Person


def create_account_cli(app):
    user_cli = AppGroup('people', help="Maintain accounts.")

    @user_cli.command('new', help="Create new person")
    @click.argument('username')
    @click.argument('password')
    @click.option('--first', help="First name")
    @click.option('--last', help="Last name")
    @click.option('--email', help="Email address")
    def create_account(username, password, first, last, email):
        first_name = first or 'Test'
        last_name = last or 'User'

        # Make sure no existing user.
        person = db.session.query(Person).filter_by(username=username).first()
        if person is not None:
            raise BadParameter(f"Already an account with username '{username}'")

        # Create the Person; commit to DB so we get ID
        person = Person(first_name=first_name, last_name=last_name, username=username, password=password, email = email)
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

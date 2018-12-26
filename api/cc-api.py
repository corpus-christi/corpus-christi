import os

import click
from click import BadParameter
from flask.cli import AppGroup

from src import create_app
from src import db
from src.i18n.models import Language, I18NLocale
from src.people.models import Person, Account
from src.people.test_people import create_multiple_people, create_multiple_accounts
from src.places.models import Country

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# ---- Data

data_cli = AppGroup('data', help="Manipulate application data.")


def _load_locales():
    locales = [
        I18NLocale(code='es-EC', desc='Español Ecuador'),
        I18NLocale(code='en-US', desc='English US')
    ]
    db.session.add_all(locales)
    db.session.commit()


@data_cli.command('load-locales', help="Load locales")
def load_locales():
    _load_locales()


@data_cli.command('load-countries', help='Load country codes')
def load_countries():
    Country.load_from_file()


@data_cli.command('load-languages', help='Load language codes')
def load_languages():
    Language.load_from_file()


@data_cli.command('load-all', help='Load everything')
def load_languages():
    _load_locales()
    Country.load_from_file()
    Language.load_from_file()
    create_multiple_people(db, 17)
    create_multiple_accounts(db, 0.25)


@data_cli.command('clear-all', help="Clear all data; drops and creates all tables")
def clear():
    db.drop_all()
    db.create_all()


app.cli.add_command(data_cli)

# ---- Users and Accounts

user_cli = AppGroup('account', help="Maintain account data.")


@user_cli.command('new', help="Create new account")
@click.argument('username')
@click.argument('password')
@click.option('--full-name', help="Full name (e.g., 'Fred Ziffle')")
def create_account(username, password, full_name):
    first_name = 'Test'
    last_name = 'User'
    if full_name is not None:
        name_parts = full_name.split()
        if len(name_parts) != 2:
            raise BadParameter(f"Can't split {full_name} into first and last")
        first_name, last_name = name_parts

    # Make sure no existing user.
    person = db.session.query(Account).filter_by(username=username).first()
    if person is not None:
        raise BadParameter(f"Already an account with username '{username}'")

    # Create the Person; commit to DB so we get ID
    person = Person(first_name=first_name, last_name=last_name)
    account = Account(username=username, password=password, person=person)
    db.session.add(account)
    db.session.commit()
    print(f"Created {person}")
    print(f"Created {account}")


@user_cli.command('password', help="Set password")
@click.argument('username')
@click.argument('password')
def update_password(username, password):
    person = db.session.query(Account).filter_by(username=username).first()
    if person is None:
        raise BadParameter(f"No account with username '{username}'")

    person.password = password
    db.session.commit()
    print(f"Password for '{username}' updated")


app.cli.add_command(user_cli)

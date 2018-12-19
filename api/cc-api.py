import os

from flask.cli import AppGroup

from src import create_app
from src.db import Base
# from src.i18n.models import Language
# from src.i18n.test_i18n import seed_database
from src.places.models import Country

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# class I18NModels:
#     locale = I18NLocale
#     key = I18NKey
#     value = I18NValue

# @app.shell_context_processor
# def make_shell_context():
#     return dict(orm=orm, i18n=I18NModels)


data_cli = AppGroup('data', help="Manipulate application data")


# @data_cli.command('load-seed', help="Load sample data")
# def seed():
#     seed_database(orm.session)


@data_cli.command('load-countries', help='Load country codes')
def load_countries():
    Country.load_from_file()


# @data_cli.command('load-languages', help='Load language codes')
# def load_languages():
#     Language.load_from_file()


@data_cli.command('drop-all', help="Drop all database tables")
def drop_all():
    Base.metadata.drop_all()


@data_cli.command('create-all', help="Create all database tables")
def create_all():
    Base.metadata.create_all()


@data_cli.command('clear', help="Clear all data; drops and creates all tables")
def clear():
    Base.metadata.drop_all()
    Base.metadata.create_all()


app.cli.add_command(data_cli)

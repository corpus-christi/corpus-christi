import os

from flask.cli import AppGroup

from src import create_app, db
from src.i18n.models import Language
from src.i18n.test_i18n import seed_database
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


@data_cli.command('load-seed', help="Load sample data")
def seed():
    seed_database(db.session)


@data_cli.command('load-countries', help='Load country codes')
def load_countries():
    Country.load_from_file()


@data_cli.command('load-languages', help='Load language codes')
def load_languages():
    Language.load_from_file()


@data_cli.command('load-all', help='Load everything')
def load_languages():
    seed_database(db)
    Country.load_from_file()
    Language.load_from_file()


@data_cli.command('clear', help="Clear all data; drops and creates all tables")
def clear():
    db.drop_all()
    db.create_all()


app.cli.add_command(data_cli)

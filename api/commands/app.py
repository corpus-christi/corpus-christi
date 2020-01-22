# Needed for pruning events

from flask.cli import AppGroup
from src import db
from src.attributes.models import Attribute
from src.i18n.models import Language, I18NLocale
from src.people.models import Role
from src.places.models import Country



def create_app_cli(app):
    app_cli = AppGroup('app', help="Maintain application-wide data.")

    def _load_locales():
        locales = [
            I18NLocale(code='es-EC', desc='Español Ecuador'),
            I18NLocale(code='en-US', desc='English US')
        ]
        db.session.add_all(locales)
        db.session.commit()

    @app_cli.command('load-locales', help="Load locales")
    def load_locales():
        _load_locales()

    @app_cli.command('load-countries', help='Load country codes')
    def load_countries():
        Country.load_from_file()

    @app_cli.command('load-languages', help='Load language codes')
    def load_languages():
        Language.load_from_file()

    @app_cli.command('load-roles', help='Load roles')
    def load_roles():
        Role.load_from_file()

    @app_cli.command('load-attribute-types', help='Load attribute types')
    def load_attribute_types():
        Attribute.load_types_from_file()

    @app_cli.command('load-all', help='Load everything')
    def load_all():
        _load_locales()
        Country.load_from_file()
        Language.load_from_file()
        Role.load_from_file()
        Attribute.load_types_from_file()

    @app_cli.command('clear-all', help="Clear ALL data - DANGEROUS")
    def clear():
        db.drop_all()
        db.create_all()

    app.cli.add_command(app_cli)

import click
from flask.cli import AppGroup

from api.src import db
from api.src.attributes.models import Attribute
from api.src.i18n.models import Language, I18NLocale
from api.src.people.models import Role
from api.src.places.models import Country


def no_rows(model):
    count = db.session.query(model).count()
    if count:
        click.echo(f"{model.__name__} count is {count}; skipping")
    else:
        click.echo(f"No {model.__name__}; loading")
    return count == 0


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
        if no_rows(I18NLocale):
            _load_locales()

    @app_cli.command('load-countries', help='Load country codes')
    def load_countries():
        if no_rows(Country):
            Country.load_from_file()

    @app_cli.command('load-languages', help='Load language codes')
    def load_languages():
        if no_rows(Language):
            Language.load_from_file()

    @app_cli.command('load-roles', help='Load roles')
    def load_roles():
        if no_rows(Role):
            Role.load_from_file()

    @app_cli.command('load-attribute-types', help='Load attribute types')
    def load_attribute_types():
        if no_rows(Attribute):
            Attribute.load_types_from_file()

    @app_cli.command('clear-all', help="Clear ALL data - DANGEROUS")
    def clear():
        db.drop_all()
        db.create_all()

    @app_cli.command('load-all', help="Load all meta data")
    def load_all():
        if no_rows(I18NLocale):
            _load_locales()
        if no_rows(Country):
            Country.load_from_file()
        if no_rows(Language):
            Language.load_from_file()
        if no_rows(Role):
            Role.load_from_file()
        if no_rows(Attribute):
            Attribute.load_types_from_file()

    app.cli.add_command(app_cli)

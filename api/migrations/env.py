from __future__ import with_statement
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Import all models so that Base.metadata includes them all
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from src.db import Base

# Import all model modules to populate Base.metadata
import src.auth.models
import src.i18n.models
import src.places.models
import src.images.models
import src.people.models
import src.attributes.models
import src.events.models
import src.teams.models
import src.assets.models
import src.groups.models
import src.courses.models

target_metadata = Base.metadata

# Override sqlalchemy.url from pydantic settings
config.set_main_option('sqlalchemy.url', settings.database_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    except Exception as exception:
        logger.error(exception)
        raise exception
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

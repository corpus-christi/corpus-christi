import os

from commands.people import create_account_cli
from commands.app import create_app_cli
from commands.courses import create_course_cli
from commands.events import create_event_cli
from commands.faker import create_faker_cli

from src import create_app

app = create_app(os.getenv('CC_CONFIG') or 'default')

create_account_cli(app)
create_app_cli(app)
create_course_cli(app)
create_event_cli(app)
create_faker_cli(app)

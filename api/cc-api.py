import os

from src.cli.app import create_app_cli
from src.cli.courses import create_course_cli
from src.cli.events import create_event_cli
from src.cli.faker import create_faker_cli
from src.cli.groups import create_group_cli
from src.cli.i18n import create_i18n_cli
from src.cli.people import create_account_cli
from src import create_app

app = create_app(os.getenv('CC_CONFIG') or 'default')

create_account_cli(app)
create_app_cli(app)
create_course_cli(app)
create_event_cli(app)
create_group_cli(app)
create_faker_cli(app)
create_i18n_cli(app)

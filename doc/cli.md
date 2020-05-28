# Corpus Christi CLI

Corpus Christi includes a command-line interface (CLI)
that extends the standard `flask` command with
CC-specific functions.
Following the default structure of the `flask` command,
CC-specific commands are grouped into several sub-commands.

To get a list of all sub-commands, run
```bash
flask --help
```
To get help on a sub-command, run
```bash
flask <subcommand> --help
```

Source code for each of the CC-specific sub-commands
is located in the `api/commands` directory.

Following is documentation of each sub-command.

## `app` - Manage application-wide data

These commands manage application-wide data.
The application will not function correctly
all application-wide data are loaded.
- `clear-all` - Clear **all** data; use with **CAUTION** 
- `load-attribute-types` - load `person` attribute types
- `load-countries` - load `country` codes
- `load-languages` - load `language` codes
- `load-locales` - load `locale` codes
- `load-roles` - load user roles

## `courses` - Manage course data

Commands to manage data for the `courses` module.
- `create-course` - create a new course
- `create-diploma` - create a new diploma

## `db` - Perform database migrations

This command is implemented by Flask itself.
Refer to the Flask documentation.

## `events` - Manage events

Manage data related to the `events` module.
- `event-demo` - create seed data for event demo
- `prune-events` - deactivate events that ended before <pruningOffset>

## `faker` - Load fake data for testing

Most modules contain functions that create fake data
for testing, debugging, and demonstrations.
- `courses` - generate fake courses
- `events` - generate fake events
- `groups` - generate fake groups
- `images` - generate fake images
- `people` - generate fake people
- `places` - generate fake places

## `people` - Manage people

These sub-commands manage data for the `people` module.
- `new` - create a new `person`
- `password` - change the password for an existing `person`

## `routes` - Show all routes

This command is implemented by Flask itself.
Refer to the Flask documentation.

## `run` - Run development server

This command is implemented by Flask itself.
Refer to the Flask documentation.

## `shell` - Run shell in app context

This command is implemented by Flask itself.
Refer to the Flask documentation.

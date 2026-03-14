# Developing Corpus Christi

This document lays out the details
of the development tools and environment
you will need to contribute to Corpus Christi (CC).

For more details on the development methodology
of the core team (including learning resources),
refer to `doc/sdm.md`.

- [Developing Corpus Christi](#developing-corpus-christi)
  - [Requirements](#requirements)
  - [Install CC](#install-cc)
    - [Clone](#clone)
    - [UI Dependencies](#ui-dependencies)
    - [Vue Dev Tools](#vue-dev-tools)
    - [API Dependencies](#api-dependencies)
  - [Environment Configuration](#environment-configuration)
  - [Database Setup](#database-setup)
    - [PostgreSQL](#postgresql)
    - [Create Database User and Database](#create-database-user-and-database)
    - [PostgreSQL with Docker](#postgresql-with-docker)
    - [Database Connection](#database-connection)
    - [Database Initialization](#database-initialization)
  - [Run CC](#run-cc)
  - [Source Code Structure](#source-code-structure)
  - [Boilerplate](#boilerplate)
  - [User Interface Internationalization](#user-interface-internationalization)
    - [Code](#code)
    - [Data](#data)
    - [Tooling](#tooling)
  - [Authentication with JSON Web Tokens](#authentication-with-json-web-tokens)
  - [Visual Studio Code](#visual-studio-code)

## Requirements

The development tool chain requires the following software.

  - [Python](https://www.python.org/) 3.11 or later
  - [uv](https://docs.astral.sh/uv/) — Python package and project manager
  - [Node](https://nodejs.org/) 18 LTS or later
  - [pnpm](https://pnpm.io/) — Node package manager
  - [Bash](https://www.gnu.org/software/bash/) current version

Windows additional downloads:

  - The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
    + Note that downloading from the Microsoft store works well.

_About Bash_: These instructions assume that you use
a `bash` shell. If you are using Windows command line
or other non-`bash` shell,
your actual mileage may vary.
You may want to try one of:
1. The [Cygwin](https://www.cygwin.com/) environment,
   which provides a workable implementation
   of many Unix/Linux commands on Windows,
   _including_ `bash`
1. The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about)

## Install CC

Instructions for installing and configuring CC.

### Clone

Clone the [CC Repository](https://github.com/corpus-christi/corpus-christi)
from GitHub to a suitable location on your workstation.
For clarity,
we'll refer to the top-level directory as `corpus-christi`

### UI Dependencies

Install the UI dependencies using pnpm:
```bash
$ cd corpus-christi/ui
$ pnpm install
```

### Vue Dev Tools

Install the [Vue Development Tools](https://github.com/vuejs/vue-devtools),
an extension for your browser that helps with Vue debugging.
Native extensions are available for Chrome (and hence, Brave) and Firefox.
There is also a standalone Electron app,
but you are _strongly_ encouraged to install Chrome, Brave, or Firefox
and the native extension.

### API Dependencies

The API uses [uv](https://docs.astral.sh/uv/) for dependency management.
First, install uv if you haven't already:
```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install all API dependencies (uv creates and manages the virtual environment automatically):
```bash
$ cd corpus-christi/api
$ uv sync --extra dev
```

That's it — no manual virtual environment setup required.
To run any command in the managed environment, prefix it with `uv run`:
```bash
$ uv run pytest
$ uv run uvicorn cc-api:app --reload
```

## Environment Configuration

The API is configured via environment variables (no `private.py` required).
Copy the sample file and fill in your values:
```bash
$ cd corpus-christi/api
$ cp .env.sample .env
```

Key variables in `.env`:
```
PSQL_USER=arco
PSQL_PASS=password
PSQL_HOST=localhost
PSQL_DB=cc-dev
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-flask-secret
CC_ENV=dev
```

The `.env` file is listed in `.gitignore` — never commit it.

## Database Setup

Be sure you have [set up your shell](#bash-setup-for-flask).

### PostgreSQL

CC uses [PostgreSQL](https://www.postgresql.org/).
You will need access to a Postgres server,
which can be a network resource
or you can install PostgreSQL on your own machine.

If you want to install PostgreSQL on your own box,
find installers
on the [official downloads page](https://www.postgresql.org/download/).
1. For the [**Mac**](https://www.postgresql.org/download/macosx/),
   I have had good luck with:
   * [Postgres.app](https://postgresapp.com/),
     which is super simple and _just works_,
   * Homebrew (my preference)
     requires that you first [install Homebrew](https://brew.sh/),
     then use Homebrew to install Postgres (`brew install postgresql`).
1. For **Windows** (if using a Windows Subsystem for Linux), switch to [this tutorial](./postgres-windows.md)).
<!-- https://github.com/corpus-christi/corpus-christi/blob/development/doc/postgres-windows.md -->
There are several installers for [**Windows**](https://www.postgresql.org/download/windows/).
1. For **Linux**, choose the appropriate distribution
   from the [main downloads page](https://www.postgresql.org/download/).

### Create Database User and Database

Once Postgres is installed,
you need to create a user and a database.
An easy way to do this is to use the shell commands
that come with Postgres.

#### Local Postgres Installation

If you run Postgres locally,
you should have access to Postgres-provided
executables that create users and databases.

Create a user:
```bash
$ createuser arco
```

Windows people (in the Subsystem, in psql):
```bash
$ CREATE USER arco;
```

Note that this creates a database user with **no password**.
This is **only** suitable for local development!
For a production system, use a good password.

Create a database:
```bash
$ createdb --owner=arco cc-dev
```

Windows:
```bash
CREATE DATABASE "cc-dev" OWNER arco;
```
- Windows: if errors, check the postgreSQL WSL installation tutorial [Tips/Debugging](./postgres-windows.md#tips--debugging) section for help.
- In psql you can run `\l` (lowercase L) to see all of the databases and owners.

This will create a database called `cc-dev`,
which is used by the default `development` configuration.
Other possibilities are:
- Testing: `cc-test`
- Staging: `cc-staging`
- Production: `cc-prod`

#### Network Postgres Access

If you are accessing Postgres over a network connection,
consult your local Postgres expert. 

### PostgreSQL with Docker

If your machine runs [Docker](https://www.docker.com/),
you may prefer to run Postgres in a Docker container.
The `docker-compose.yaml` file contains a simple configuration
that should spin up a Postgres database server
when you run
```bash
$ docker-compose up --detach
```
from the directory containing the `docker-compose.yaml` file.

The configuration exposes port `5432`
(the Postgres default port) from the container,
allowing you to connect to the database using `psql`
or another Postgres database client
(e.g., [DataGrip](https://www.jetbrains.com/datagrip/)).

To connect from `psql` with the configuration found in `docker-compose.yaml`, run:
```bash
$ psql --host=localhost --user=arco cc-dev
```
and provide `password` as the password when prompted.

Note that you **must** provide the `--host` argument
in order to force `psql` to connect over a TCP socket.
By default, `psql` uses a Unix-domain socket,
which works great for a local Postgres server
but not for one running in a Docker container.

Important notes:

1. You do _not_ need to set up a Postgres user or database manually
   when using docker.
   They will be created automatically
   according to the configuration in the `docker-compose.yaml` file.
1. Take care not to try to run 
   two Postgres servers listening on the same port.

### Database Connection

Set the database connection via environment variables in your `.env` file
(see [Environment Configuration](#environment-configuration)):

```
PSQL_USER=arco
PSQL_PASS=password
PSQL_HOST=localhost
PSQL_DB=cc-dev
```

For testing, set `PSQL_DB=cc-test` or override with `DATABASE_URL` directly:
```
DATABASE_URL=postgresql://arco:password@localhost/cc-test
```

### Database Initialization

Run Alembic migrations and load seed data using the CLI:
```bash
$ cd corpus-christi/api
$ uv run alembic upgrade head
$ uv run cc-cli app load-all
```

To completely reset the database during development:
```bash
$ uv run cc-cli app reset-db
```

Once the database is initialized, create a CC account for yourself:
```bash
$ uv run cc-cli people new-account --first="Fred" --last="Ziffle" username password
```
where
- `--first` is the user's first name (optional)
- `--last` is the user's last name (optional)
- `username` is the username for the account
- `password` is the password for the account

## Run CC

For development, you need to run *two* servers
to work with CC.
Run each process in _it's own_ shell
and leave these shell windows open.
The servers produce useful debugging information
when things go haywire.

1. Start the API server
    ```bash
    $ cd corpus-christi/api
    $ uv run uvicorn cc-api:app --reload --port 5000
    ```
   You should see uvicorn start and report the address it is serving on.
   The interactive API docs are available at `http://localhost:5000/docs`.

1. **In a separate shell**, start the Vue dev server
    ```bash
    $ cd corpus-christi/ui
    $ pnpm dev
    ```
   You should see Vite build the app and print the local URL to connect to the UI.

## Source Code Structure

The structure of the CC source code is as follows:

- `api/` - RESTful API server based on [FastAPI](https://fastapi.tiangolo.com/).
    - `bin/` - Utility executables
    - `migrations/` - database migrations created by Alembic
    - `src/` - Main API source;
      Directories within `src` contain subsets of the API
      divided into manageable modules.
      The common structure within each module
      is documented under `i18n`.
      - `auth/` - Authentication endpoints and JWT dependencies
      - `boilerplate/` - See [Boilerplate details](#boilerplate)
      - `etc/` - Endpoints that don't fit anywhere else.
      - `groups/` - Endpoints for the home groups module
      - `i18n/` - API endpoints for Internationalization;
        like most directories under `src`,
        contains the following files:
        - `__init__.py` marks this directory as a Python _package_
          and exports the FastAPI `APIRouter`
        - `api.py` contains the API route handlers for this module
        - `models.py` implements database _models_ using SQLAlchemy 2
          and Pydantic v2 schemas for request/response validation.
        - `test_i18n.py` contains tests for this package
          using the Pytest library.
       - `people/` - API for the people and accounts
       - `places/` - API for locations and countries
       - `shared/` - Common API functions and dependencies
       - `__init__.py` - Marks `src` as a Python package;
         creates the FastAPI application and registers all routers.
       - `conftest.py` - Contains configuration for testing the API
         using [Pytest](https://docs.pytest.org/en/latest/contents.html#toc)
         and FastAPI's `TestClient`.
       - `db.py` - SQLAlchemy 2 engine, session factory,
         and `get_db` dependency.
       - `test_basics.py` - Basic tests not related to a particular endpoint.
     - `cc-api.py` - Top-level entry point; exposes the FastAPI `app` for uvicorn.
     - `cli.py` - Typer CLI entry point (`uv run cc-cli`).
     - `config.py` - Pydantic Settings; reads configuration from environment variables.
     - `pyproject.toml` - Project metadata, dependencies, and tool configuration.
     - `uv.lock` - Locked dependency versions for reproducible installs.
- `doc/` - Project-wide documentation
- `ui/` - User interface - [Vue](https://vuejs.org/) single-page web app
  - `assets/` - Graphics files, other static asset files
  - `i18n/` - See [UI I18N](#user-interface-internationalization)
  - `public/` - Top-level files serve directly to client browser
  - `src/` Source files for the UI
    - `components/` - "Small", reusable components
      that make up parts of pages (e.g., the locale menu)
    - `models/` - "View Models"; plain-old JavaScript classes
      used to store data that's passed around the UI code
      (e.g., `Account` represents the curent user)
    - `pages/` - Top-level "pages" that make up the UI.
      Because CC's UI is a single-page application,
      it would be better to call these
      "views," but that term is already overloaded.
    - `plugins/` - Convenient gathering place for various
      additions to the base Vue configuration
    - `App.vue` - The top-level Vue module
    - `flags.js` - Assored JavaScript functions that don't really belong anywhere else
    - `main.js` - The main function that's invoked at UI startup;
      includes all the other pieces and parts,
      creates the main Vue object.
    - `router.js` - Configuration for the client-side router,
      based on [Vue Router](https://router.vuejs.org/)
    - `store.js` - UI global state,
      using [Vuex](https://vuex.vuejs.org/)
  - `tests/` contains end-to-end tests using
    [Cypress](https://www.cypress.io/)
  - `*.config.js`, `*rc.js`, `*.json` - Configuration files for various modules
  - `package.json` - NPM configuration file for the UI;
    also defines `scripts` that can be invoked by `yarn`.
- `.editorconfig` - Editor configuration to help maintain
  code formatting consistency
- `.gitignore` - Patterns of files and directories
  to be excluded from Git

## Boilerplate

In the API of any CRUD application,
there is often a significant amount of
repetitious code
(e.g., create an `X`, read an `X`, delete an `X`).
To make it easier to write these
"stereotypical" functions,
CC includes a "boilerplate" mechanism.
The idea is this:
1. Create a file that declares the structure of some application data.
1. Run a program (`boil.py`) that converts the structure into code for:
   1. A SQLAlchemy model
   1. A Marshmallow validator
   1. API endpoints
   1. Test functions
1. Use the output from `boil.py` as a _starting place_
   for coding the API

Find the `boil.py` program and some configuration files
in `api/src/boilerplate`.

The input files for `boil.py`
are in [YAML](https://yaml.org/) format,
a simple and readable representation of
common program structures like arrays and dictionaries.
Find examples in the `.../boilerplate/yaml` directory.
You should create new `boil.py` configurations
in this directory and _include them in revision control_.

The `boil.py` program validates the YAML input files
using (JSON Schema)[http://json-schema.org/].
The schema is self-documenting;
refer to the `schema` structure
in `boil.py` for details on the proper format for
the YAML input file.

To process the YAML file, run:
```bash
$ cd api/src/boilerplate
$ ./boil.py yaml/your-yaml-file
```
The `boil.py` program simply prints to `stdout`.
You can copy-paste the output into the appropirate
files in the API source code as desired.
The program is _not_ designed to update source
files directly, which could cause loss of code.
It generates _starter code_
that you should check, enhance, augment, etc.

## User Interface Internationalization

From the ground-up, CC is internationalized
and localizable.
_No user-visible output
should ever be hardcoded in a particular language._
Instead, we use the [Vue I18n](https://kazupon.github.io/vue-i18n/)
module to provide localization.

Find all of the files referenced here
in the directory
`corpus-christi/ui/i18n`

### Code

The Vue I18n library exposes several functions
that facilitate localization.
The most important one is called `$t`
(the `t` stands for "translate").

Whenever you would normally insert literal text
in just one language, use `$t` instead.
Here's an example from a Vue `<template>`:
```javascript
{{ $t('person.name.first') }}
```
This snippet asks Vue I18n to
look up the text for `person.name.first`
in the current language locale
and return it as the value of the function.
Similarly, here's how to call this function in a Vue `<script>`:
```javascript
this.$t('person.name.first')
```

Note that the identifier passed to `$t`
is "dotted": it allows you to specify
a hierarchy of localization information.
In CC, one way we use this is to separate
localization data by the top-level modules
(e.g., `groups`, `calendar`, etc.)

### Data

The data used by Vue I18n
is formatted as nested JavaScript objects.
The keys of the top-level object
are language identifiers (e.g., `en` for English
and `es` for Spanish).
Within the top level,
the data are hierarchical according to the
"dotted" syntax of the identifiers.
See the [Vue I18n documentation]
for an example.

This format works great at run time
but isn't ideal for developers.
Instead,
we'd like to have the data structured
with the "dotted" values in the outermost objects,
then store the translated strings
at the leaf nodes.
This approach puts all the localizations
for a given "dotted" value
at the same node of the hierarchy.

Here's an example:

    person:
      name:
        first:
          en: First Name
          es: Nombre de pila
        last:
          en: Last Name
          es: Apellido

This snippet shows the localizations
for `person.name.first` and `person.name.last`.
Note that the `en` and `es` nodes appear together
for each of the dotted values,
making it simple to see how this particular
string is being localized in all supported languages.

Data files for localization should be stored
at `...i18n/yaml`
in [YAML](https://yaml.org/) files.
These files _should_ be in revision control.

### Tooling

The `i10n-to-i18n.py` program
converts the developer-friendly
format of the YAML files
into a JSON file suitable for Vue I18n.

There is a `package.json` script
that runs this program.
After updating/adding your localization
data in a YAML file:
```bash
$ cd corpus-christi/ui
$ yarn localize
```
This command reads all the YAML files
and generates the One True L10N file
`corpus-christi/i18n/cc-i18n.json`.
The Vue I18N configuration
reads this file at run-time.

## Authentication with JSON Web Tokens

CC uses JSON Web Tokens for authentication. How it works:
1. User clicks a Log In link.
1. UI prompts for username and password
1. UI sends username and password to API
1. API validates username and password against database
1. API returns a JSON Web Token (JWT) to UI
1. UI stores JWT in memory and in browser local storage for later use
1. Any time the UI wants to connect to a protected endpoint,
   it includes the JWT as an HTTP header in the request
1. API endpoint validates JWT before executing endpoint code.

Most, but not all, CC endpoints are protected by JWT.
UI requests to an authenticated endpoint
use the `$http` object
and those to an unauthenticated endpoint (e.g., log in)
use the `$httpNoAuth` object.

Similarly for testing the API,
there are two Flask client objects:
1. `auth_client` includes a JWT for testing authenticated endpoints
1. `plain_client` does _not_ have a JWT and is used to test unauthenticated endpoints
Using the wrong client results an an exception from the endpoint.

## Visual Studio Code

For development with Visual Studio Code,
consider installing the `ms-python.python` extension.
uv manages the virtual environment at `api/.venv` —
point VS Code to that interpreter:
```
corpus-christi/api/.venv/bin/python
```

Useful extensions:
- `ms-python.python` — Python language support
- `ms-python.pylint` — Linting
- `charliermarsh.ruff` — Fast linter/formatter (replaces autopep8)


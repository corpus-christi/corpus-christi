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
  - [Bash Setup for Flask](#bash-setup-for-flask)
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
- [Python](https://www.python.org/) 3.7 or later
- [Node](https://nodejs.org/) 10 LTS or later
- [Yarn](https://yarnpkg.com/) current version
- [Bash](https://www.gnu.org/software/bash/) current version

_About Bash_: These instructions assume that you use
a `bash` shell. If you are using Windows command line
or other non-`bash` shell,
your actual mileage may vary.
You may want to try installing
the [Cygwin](https://www.cygwin.com/)
environment,
which provides a workable implementation
of many Unix/Linux commands on Windows,
_including_ `bash`.

## Install CC

Instructions for installing and configuring CC.

### Clone

Clone the [CC Repository](https://github.com/corpus-christi/corpus-christi)
from GitHub to a suitable location on your workstation.
For clarity,
we'll refer to the top-level directory as `corpus-christi`

### UI Dependencies

Install the UI dependencies, of which there are _many_.
Installation takes several minutes.
```bash
$ cd corpus-christi/ui
$ yarn install
```

### Vue Dev Tools

Install the [Vue Development Tools](https://github.com/vuejs/vue-devtools),
an extension for your browser that helps with Vue debugging.
Native extensions are available for Chrome and Firefox.
There is a standalone Electron app,
but you are _strongly_ encouraged to install Chrome or Firefox
and the native extension.

### API Dependencies

1. Create a Python virtual environment; you only need to do this once
    ```bash
    $ cd corpus-christi/api
    $ python3 -m venv venv
    ```
1. Activate the virtual environment;
   you need to do this _whenever_ you start a new shell
   in which you want to work on CC.
    ```bash
    $ source venv/bin/activate
    ```
1. Check that your virtual environment is set up properly
    ```bash
    $ which pip
    ```
    should respond with a path that is _inside_ the virtual environment.
1. Install the required Python packages
    ```bash
    $ pip install -r requirements.txt
    ```

Note that when you are done interacting with the API,
you can _deactivate_ your virtual environment
by entering this simple command
```bash
$ deactivate
```
This will remove the virtual environment from your shell.

## Bash Setup for Flask

Flask (on which the API is written)
includes a handy utility command
called `flask`.
To make it easy to use this command during development,
set up your `bash` shell
as follows:
```bash
$ cd corpus-christi/api
$ source ./bin/set-up-bash.sh
```
This script will
1. Activate your virtual environment
1. Configure Flask properly for development
1. Allow you to run the `flask` command from the command line.
Do this whenever you start a new `bash`
in which you intend to work with the API.

## Database Setup

Be sure you have [set up your shell](#bash-setup-for-flask-api).

### PostgreSQL

CC uses [PostgreSQL](https://www.postgresql.org/).
You will need access to a Postgres server,
which can be either a network resource
or you can install a server on your own machine.

Locate installers for Postgres
on the [official downloads page](https://www.postgresql.org/download/).
1. For the [**Mac**](https://www.postgresql.org/download/macosx/),
   I have had good luck with both [Postgres.app](https://postgresapp.com/),
   which is super simple and _just works_,
   and the Homebrew version (which is my preference).
   The latter requires that you first [install Homebrew](https://brew.sh/)
   and then use Homebrew to install Postgres (`brew install postgresql`).
1. There are several installers for [**Windows**](https://www.postgresql.org/download/windows/).
   If you have experience or preferences here,
   please feel free to update this documentation with your recommendations.
   * If you are using a Windows Subsystem for Linux (e.g. Ubuntu for Windows) or something of the like, follow this [**tutorial**](https://github.com/corpus-christi/corpus-christi/blob/development/doc/postgres-windows.md)).
1. For **Linux**, choose the appropriate distribution
   from the [main downloads page](https://www.postgresql.org/download/).

### Create Database User and Database

Once Postgres is installed,
you need to create a user and a database.
An easy way to do this is to use the shell commands
that come with Postgres.
Create a user:
```bash
$ createuser arco
```
Note that this creates a database user with **no password**.
This is **only** suitable for local development!
For a production system, use a good password.

Create a database:
```bash
$ createdb --owner=arco cc-dev
```
This will create a database called `cc-dev`,
which is used by the default `development` configuration.
Other possibilities are:
- Testing: `cc-test`
- Staging: `cc-staging`
- Production: `cc-prod`

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
1. Be careful not to run two Postgres servers listening on the same port.

### Database Connection

The values that you supply for Postgres user, password, host, etc.
should match the values supplied in the `api/private.py` file.
A default file is included with the CC repository
that should work with the default configuration.
Update it as appropriate for your use case.
If you are configuring CC for production use,
*do not* commit the updated `private.py` file
to a public Git repository.
The file is included in the CC `.gitignore` file,
so it should not be added to commits.

### Database Initialization

Use the `flask` command to initialize your development database:
```bash
$ flask db migrate
$ flask db upgrade
$ flask data load-all
```

To completely reset the database during development,
the script `bin/reset-db.sh` may be of use.

Once the database is initialized,
create a test account for yourself.
```bash
$ flask account new --first="Fred" --last="Ziffle" username password
```
where
- `--first` is the user's first name
- `--last` is the user's last name
- `username` is the user name of the account
- `password` is the password to be associated with the account
The `--first` and `--last` flags are _optional_.
To include a first or last name with blanks or other
characters special to the shell,
enclose it in quotes. For example:
```bash
$ flask account new --first="Billy Bob" --last="Smith" bbob bob-pass
```

## Run CC

For development, you need to run two servers
to work with CC.
Run each process in _it's own_ shell
and leave these shell windows open.
The servers produce useful debugging information
when things go haywire.

1. Start the API server
   (be sure you have [set up your shell](#bash-setup-for-flask-api))
    ```base
    $ cd corpus-christi/api/bin
    $ ./run-dev-server.sh
    ```
   You should see a few lines indicating that
   Flask is serving the application.
   (You can also use `flask` directly; the script above is just
   a thin wrapper around the `flask` command.)
1. Start the Vue CLI service
    ```bash
    $ cd corpus-christi/ui
    $ yarn serve
    ```
   You should see the application being built
   then a `Compiled successfully` message
   and the URLs where you can connect to the UI.

## Source Code Structure

The structure of the CC source code is as follows:

- `api/` - RESTful API server based on [Flask](http://flask.pocoo.org/).
    - `bin/` - Utility executables
    - `migrations/` - database migrations created by Alembic
    - `src/` - Main API source;
      Directories within `src` contain subsets of the API
      divided into managable modules.
      The common structure within each module
      is documented under `i18n`.
      - `auth/` - Authentication endpoints
      - `boilerplate/` - See [Boilerplate details](#boilerplate)
      - `etc/` - Endpoints that don't fit anywhere else.
      - `groups/` - Endpoints for the home groups module
      - `i18n/` - API endpoints for Internationalization;
        like most directories under `src`,
        contains the following files:
        - `__init__.py` marks this directory as a Python _package_;
          includes initialization code to help integrate
          this package into the overall application
        - `api.py` contains the portion of the API endpoints
          for this module
        - `models.py` implements database _models_
          (in the Model-View-Controller sense)
          based on SQLAlchemy and Marshmallow.
        - `test_i18n.py` contains tests for this package,
          using the Pytest library.
          Note that the file is named consistently
          with the package name.
       - `people/` - API for the people and accounts
       - `places/` - API for locations and countries
       - `roles/` - API for CC roles
       - `shared/` - Common API functions
       - `__init__.py` - Marks `src` as a Python package.
         This is where all API initialization takes place.
       - `conftest.py` - Contains configuration for testing the API
         using [Pytest](https://docs.pytest.org/en/latest/contents.html#toc)
       - `db.py` - Configuration information for database access
         using [SQL Alchemy](https://www.sqlalchemy.org/)
       - `test_basics.py` - Basic tests not related to a particular endpoint.
     - `cc-api.py` - Top-level Python file for the API.
       Also implements extensions to the `flask` command.
     - `config.py` - Configuration of various Flask
       parameters for use in development, testing, and production.
     - `Makefile` - Handy command-line commands
     - `pytest.ini` - Configuration for the `pytest` test suite.
     - `requirements.txt` - Python packages required for the API
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
    - `helpers.js` - Assored JavaScript functions that don't really belong anywhere else
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
To make full use of the extension,
be sure to install Python modules as follows
_in the virtual environment_.

1. `pip install pylint`
1. `pip install autopep8`

Note that, as of this writing,
you must run these `install` commands manually.
Choosing `Install` from the VS Code popup
installs them in the wrong place.


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
  - [Command-Line Interface](#command-line-interface)
  - [Database Setup](#database-setup)
    - [PostgreSQL](#postgresql)
    - [Create Database User and Database](#create-database-user-and-database)
    - [PostgreSQL with Docker](#postgresql-with-docker)
    - [Database Connection](#database-connection)
    - [Setting up PostGIS](#setting-up-postgis)
    - [Database Initialization](#database-initialization)
  - [Run CC](#run-cc)
  - [Source Code Structure](#source-code-structure)
  - [Boilerplate](#boilerplate)
  - [User Interface Internationalization](#user-interface-internationalization)
    - [Code](#code)
    - [Database Records](#database-records)
    - [Revision Control](#revision-control)
  - [Authentication with JSON Web Tokens](#authentication-with-json-web-tokens)
  - [Visual Studio Code](#visual-studio-code)

## Requirements

The development tool chain requires the following software.

  - [Python](https://www.python.org/) 3.9 (may work on earlier versions)
  - [Node](https://nodejs.org/) 10 LTS or later
  - [Yarn](https://yarnpkg.com/) current version
  - [Bash](https://www.gnu.org/software/bash/) current version

Windows additional downloads:

  - The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
    + Note that downloading from the Microsoft store works well.

_About Bash_: These instructions assume that you use
a `bash` shell. If you are using Windows command line
or other non-`bash` shell,
your actual mileage may vary.
You may want to try one of:
1. The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about)
1. The [Cygwin](https://www.cygwin.com/) environment,
   which provides a workable implementation
   of many Unix/Linux commands on Windows,
   _including_ `bash`

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
$ yarn
```

### Vue Dev Tools

Install the [Vue Development Tools](https://github.com/vuejs/vue-devtools),
an extension for your browser that helps with Vue debugging.
Native extensions are available for Chrome (hence, Brave) and Firefox.
There is also a standalone Electron app,
but you are _strongly_ encouraged to install Chrome, Brave, or Firefox
and the native extension.

### API Dependencies

1. Create a Python virtual environment; you only need to do this once
    ```bash
    $ cd corpus-christi/api
    $ python3 -m venv venv
    ```

    Note that the `python3` command may not have the correct version.
    If you have errors with this, run `python3 --version`,
    if that is not the desired version, try running `python --version`. 
    If this is your desired version, replace `python3` with `python` 
    in the above bash commands.

    If you are still struggling (and using Windows), 
    you will need to adjust the [environmental variables](https://www.architectryan.com/2018/08/31/how-to-change-environment-variables-on-windows-10/) 
    and update PATH by finding the location of where python is downloaded.
    Open the base python folder, 
    copy that path/link and add it to PATH in the system variables.

1. Activate the virtual environment;
   you need to do this _whenever_ you start a new shell
   in which you want to work on CC.
    ```bash
    $ source venv/bin/activate
    ```
      - Note that if this is causing errors, try `source venv/Scripts/activate`

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
You can also just close the shell normally.

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
1. Activate your virtual environment;
   no need to separately `source` the `activate` command
1. Configure Flask properly for development
1. Allow you to run the `flask` command from the command line.

On Windows, you may need to open the file
and change line three to source `./venv/Scripts/activate` instead.

Do this whenever you start a new `bash`
in which you intend to work with the API.

## Command Line Interface

CC extends the standard Flask Command-Line Interface (CLI).
Refer to [the CLI documentation](./cli.md) for details.

## Database Setup

Be sure you have [set up your shell](#bash-setup-for-flask).

### PostgreSQL

CC uses [PostgreSQL](https://www.postgresql.org/).
You will need access to a Postgres server,
which can be a network resource, or
you can install PostgreSQL on your own machine.

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
$ createuser arco --pwprompt
```
The command prompts you for a password.
Enter your desired password.

In WSL, run the `psql` command and run this query:
```
CREATE USER arco WITH ENCRYPTED PASSWORD 'password';
```
Replace `password` with your desired password.

Create a database:
```bash
$ createdb --owner=arco cc-dev
```

Windows:
```
CREATE DATABASE "cc-dev" OWNER arco;
```
- Windows: if errors, check the PostgreSQL WSL installation tutorial
  [Tips/Debugging](./postgres-windows.md#tips--debugging) section for help.
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

The API server needs access to the configuration details
for things like the database connection, various security keys, and the like.
CC stores these things in a "dot-env" file, 
so-called because it lives in a file called `.env`
in the top-level server directory (`api`).

The repository contains a sample file called `sample.env`.
You should copy this into a new file, `api/.env`
and update it to match your configuration.

**IMPORTANT** These details must _never_ be committed to revision control!
If you are configuring CC for production use,
*do not* commit your `.env` file to a public repository!
To help avoid accidental commits,
`.env` is listed in the CC `.gitignore` file.
Still, **use caution**!

When you need to set up the email services for the server, if we choose the Gmail services, 
replace the `EMAIL_USERNAME` and `EMAIL_PASSWORD` with your personal email user-name and password.

> Gmail Set Up
>  1. Update the Gmail account setting. 
       Allow less security setting [URL](https://myaccount.google.com/lesssecureapps?pli=1)
       By the default, Google doesn't allow insecure apps have connections with its server.
       For security reasons, if you account already has the 2FA (Two-Factor Authentication),
       It is safer to [create a seperate Google account](https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp)
       or create [application-specific password](https://support.google.com/accounts/answer/185833)
>   2. [Display Unlock Captcha](https://accounts.google.com/DisplayUnlockCaptcha)
>   3. [Enable IMAP](https://mail.google.com/mail/#settings/fwdandpop)   


**During development and testing**,
you can override the database connection 
by defining environment variables in `bash`.
For example:
```bash
export DEV_DB_URL="postgresql://PSQL_USER:PSQL_PASS@PSQL_HOST/PSQL_DB"
```
tells CC how to connect to your development database (the `DEV` part of the environment variable)
where:
   * `PSQL_USER` is your Postgres username
   * `PSQL_PASS` is your Postgres password
     (if you haven't set a password, omit this field _and_ the colon
     that separates it from `PSQL_USER`)
   * `PSQL_HOST` is the host where the Postgres server is running
     (DNS name or `localhost` if running on your workstation)
   * `PSQL_DB` is your Postgres database name

Similarly, you can define `TEST_DB_URL` for your test database (for use with `pytest`)
or `PROD_DB_URL` for your production database.

### Setting up PostGIS

**Note**: Unless you're working on the `places` module in CC,
you probably don't need to install this extension.

Make sure you have PostGIS installed. 
See http://postgis.net/install/ for installer packages for most operating systems.

If you want to compile from source, visit http://postgis.net/source/

More detailed installation information for specific versions is available here: 
http://postgis.net/documentation/ under the Stable Branch User Documentation. 
Select the PDF or HTML corresponding to your PostGIS version and look for PostGIS Installation.

See the Enabling PostGIS section on http://postgis.net/install/ 
for instructions on enabling PostGIS on your database.

Most likely the only extension needed is `postgis`.
You can safely ignore other recommended extensions unless you have a specific use for them.

#### If you are using OSX Postgres.app 

PostGIS comes packaged with Postgres.app. 
Using these two commands from the terminal should enable PostGIS
on the specified version of Postgres.app

```bash
$ POSTGRES_VERSION = Version of Postgres you want to enable PostGIS on.
$ POSTGIS_VERSION = Your installed version of PostGIS.
$ psql -d DATABASE_NAME -f /Application/Postgres.app/Contents/Versions/POSTGRES_VERSION/share/postgresql/contrib/POSTGIS_VERSION/postgis.sql
$ psql -d DATABASE_NAME -f /Application/Postgres.app/Contents/Versions/POSTGRES_VERSION/share/postgresql/contrib/POSTGIS_VERSION/spatial_ref_sys.sql
```

#### WARNING

_Before_ you initialize the database,
make sure that after you run `flask db migrate`
you check the python migration file
(found under `api/migrations/versions/<random_numbers>.py`). 
Make sure the migration doesn't drop the `spatial_ref_sys` table added by PostGIS. 
Inside the `upgrade` function (likely near the end), 
if there is a statement to drop the `spatial_ref_sys` table, 
delete that statement. 
Also check the `downgrade` function 
and delete any code generated to add a `spatial_ref_sys` table. 
After you have done this and saved the migration file,
it is ok to run `flask db upgrade` and load data

### Database Initialization

*On Windows*: run the rest of the commands in bash and not WSL.
Make sure `api/.env` file has the correct password (password used in `psql`).
If errors, check the PostgreSQL WSL installation tutorial
[Tips/Debugging](./postgres-windows.md) section for help. 

Use the `flask` command to initialize your development database:
```bash
$ flask db migrate
$ flask db upgrade
```

To initialize the data required by the application,
you can either run a convenience shell script:
```bash
$ ./bin/load-all-app-data.sh
```
or use individual commands available
through `flask app` (run `flask app --help` to see options).

To completely reset the database during development,
the script `bin/reset-db.sh` may be of use.

Once the database is initialized,
create a CC test account for yourself.
```bash
$ flask people new --first="Fred" --last="Ziffle" username password
```
where
- `"Fred"` is the user's first name
- `"Ziffle"` is the user's last name
- `username` is the user name of the account
- `password` is the password to be associated with the account

The `--first` and `--last` flags are _optional_.
To include a first or last name with blanks or other
characters special to the shell,
enclose it in quotes. For example:

```bash
$ flask people new --first="Billy Bob" --last="Smith" bbob bbob-pass
```

If you need to test operations that require a
specific `role`, you can attach a role to the
created person with the `--roles` flag:

```bash
$ flask people new --roles role.group-admin username password
```

Use multiple `--roles` flags to attach more than one role:

```bash
$ flask people new --roles role.group-admin \
                   --roles role.translator \
                    username password
```

## Run CC

For development, you need to run *two* servers
to work with CC.
Run each process in _it's own_ shell
and leave these shell windows open.
The servers produce useful debugging information
when things go haywire.

1. Start the API server
   (be sure you have [set up your shell](#bash-setup-for-flask))
    ```base
    $ cd corpus-christi/api
    $ ./bin/run-dev-server.sh
    ```
   You should see a few lines indicating that
   Flask is serving the application.
   (You can also use `flask` directly; the script above is just
   a thin wrapper around the `flask` command.)
1. **In a separate shell**, start the Vue CLI service
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


### Database Records

During runtime, those dotted entries will be
fetched from the database according to the
currently selected locale. 

For example, if the current locale is set
to `en-US`, a dotted value `person.name.first`
might correspond to a database entry in the
`I18NValue` table that looks like the following: 

    key_id: person.name.first
    locale_code: en-US
    gloss: First Name

In this case, the user would see "First Name"
rendered in place of the original dotted string
`person.name.first`.

Likewise, if the user changes the current locale
to `es-EC`, then the application will try to
locate a database entry that looks like

    key_id: person.name.first
    locale_code: es-EC
    gloss: Nombre de pila

and render "Nombre de pila" in place of the
original dotted string.

### Revision Control

We would also like the translation entries to be
kept in the revision control, so that corrections
of translations can be tracked, and a developer
would be able to quickly populate an empty
database with existing translations.

Currently, translation entries are kept in JSON
format under the `corpus-christi/api/i18n`
directory.

To load translation entries of a particular locale
(e.g. en-US), execute the following commands:

```bash
$ cd corpus-christi/api
$ source bin/set-up-bash.sh
(venv) $ flask i18n load en-US
```

This will load all entries from a file
`corpus-christi/api/i18n/en-US.json` into the
database.

There is a corresponding "dump" command that does
the reverse, that is, exports entries from the
database into a json file.

```bash
(venv) $ flask i18n dump en-US
```

For a detailed overview on the i18n commands, see
[i18n Commands Suites](i18n-commands.md)

For more usage info, see

```bash
(venv) $ flask i18n --help
```

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


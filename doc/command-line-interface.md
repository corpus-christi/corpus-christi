# Command-Line Interface

The `flask` CLI command provides capabilities that are
helpful during development.
Some commands come with Flask
and some are specific to Corpus Christi.

Like Git, the `flask` CLI has a hierarchical command structure.
You can get help at each level of the hierarchy
with the `--help` flag.
Here are the available commands, 
listed hierarchically.
To run, for example, the `clear-all` command,
type `flask data clear-all`

- `flask`
    - `account` - manages CC accounts
        - `new` create a new account for CC
        - `password` update the password for an existing account
    - `data` - manages database content
        - `clear-all` **deletes all data** in the database by dropping and then recreating all database tables.
        - `load-countries` loads country data
        - `load-languages` loads language data
        - `load-locales` loads language locales
        - `load-all` creates all table in the data model and loads sample data.
    - `db` - handles database migrations; there are many options within `flask db`; the most relevant are:
        - `migrate` to create a new migration after updating application models
        - `upgrade` to apply a migration to the database.    
    - `maintain` - contains operations that are used to maintain the database
        - `prune-events` archives all events that have ended more than 30 days before the script is run
    - `routes` - prints a list of all routes configured in the API
    - `run` - starts the Flask server
    - `shell` - opens a Python shell set up with access to Flask objects (e.g., `request`, `session`)

# Environment Variables

Several environment variables alter how the CLI behaves.
Refer to the [Flask documentation](http://flask.pocoo.org/docs/1.0/config/)
for details.

1. `FLASK_APP` sets the top-level application executable, used, for example by `flask run`
   Normally, you will use `cc-api.py` for this variable.
1. `FLASK_ENV` can be set to `production` (the default), which disables debugging features
   or `development` which enables most debugging, warnings, etc. for use during development.
1. `FLASK_DEBUG` turns on an interactive debugging mode that is mostly useful when accessing
   a traditional (server-side rendering) Flask application. It is less useful for a RESTful API.
   A setting of `development` for `FLASK_ENV` also enables `FLASK_DEBUG`
1. `TESTING` disables Flask's processing of exceptions, allowing any exceptions thrown
   to interrupt execution, notifying you of a problem in the code.
   
You can set values for an environment variable in several ways:
1. Store it in your `.bashrc` (or related) file, 
   which will set the value for every shell you run
1. Set it at the command line, which will remain in effect
   until you either set it again or the shell exits.
   For example:
   ```bash
   $ export FLASK_ENV=production
   ```
1. Set it _on the command line_ prior to a command you're executing.
   For example:
   ```bash
   $ FLASK_APP=my-app.py FLASK_ENV=development flask run
   ``` 

# Configuration

The `corpus-christi/api/config.py` file contains a set of classes 
that configure the execution of the application,
setting appropriate values for environment variables like those mentioned above.

CC can be run in any of these modes,
each of which has a configuration identifier.
1. Testing (identifier `test`) - used when running unit or end-to-end tests
1. Development (`dev`) - used for most development work
1. Staging (`staging`) - runs the application in as close to prouction-ready state as possible
1. Production (`prod`) - production deployment
There is also an identifier `default`, which is the mode
the application runs unless otherwise specified.
Currently, it is set to the Development configuration.

To run a configuration _other_ than the `default`,
supply a value for the `FLASK_CONFIG` environment variable.
For example:
```bash
$ FLASK_CONFIG=prod flask run
```

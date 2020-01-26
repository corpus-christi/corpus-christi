#!/usr/bin/env bash

# Load all the application-wide flask data.

flask app load-locales
flask app load-countries
flask app load-languages
flask app load-roles
flask app load-attribute-types

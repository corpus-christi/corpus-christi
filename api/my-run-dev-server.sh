#!/usr/bin/env bash

export FLASK_APP=cc-api.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask data load-roles
flask run

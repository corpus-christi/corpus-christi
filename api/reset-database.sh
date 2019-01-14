#!/usr/bin/env bash

source ./venv/bin/activate

rm dev-db.sqlite
rm migrations/versions/*.py

flask db upgrade
flask db migrate
flask db upgrade
flask data load-all
flask account new --first="Fred" --last="Ziffle" username password
flask account new --first="Quality" --last="Assurance" Cytest password
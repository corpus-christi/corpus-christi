#!/usr/bin/env bash

source ./venv/bin/activate

rm dev-db.sqlite
rm migrations/versions/*.py

flask db migrate
flask db upgrade
flask course new --prereq=6 "Alone low investment" "blah blah blah"
flask data load-all
flask account new --first="Fred" --last="Ziffle" username password
flask account new --first="Quality" --last="Assurance" Cytest password

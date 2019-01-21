#!/usr/bin/env bash

source ./venv/bin/activate

rm dev-db.sqlite
rm migrations/versions/*.py

flask db migrate
flask db upgrade
flask data load-all
flask account new --first="Fred" --last="Ziffle" username password
flask course new --prereq=6 --offering="Around happy fast" "Alone low investment" "blah blah blah"
flask diploma new "Above" "blah blah blah"
flask account new --first="Quality" --last="Assurance" Cytest password

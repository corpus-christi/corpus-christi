#!/usr/bin/env bash

source ./venv/bin/activate

export FLASK_APP=cc-api.py
export FLASK_ENV=development

PROMPT=$(which fancy-prompt.py)
if [[ -x $PROMPT ]]
then
    PS1=`$PROMPT`
fi

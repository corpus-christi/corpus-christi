#!/usr/bin/env bash

export FLASK_APP=cc-api.py
export FLASK_ENV=development

flask $*

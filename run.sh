#!/usr/bin/env bash

export FLASK_APP=cc-main.py
export FLASK_ENV=development

flask $*

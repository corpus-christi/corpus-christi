#!/usr/bin/env bash

# Combine all the YAML input files into a single JSON
# file containing all localizations for CC.

EXEC='./l10n-to-i18n.py'
IN_FILE_GLOB='./yaml/*-l10n.yaml'
OUT_FILE='./cc-i18n.json'

$EXEC $IN_FILE_GLOB > $OUT_FILE

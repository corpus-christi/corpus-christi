#!/usr/bin/env bash

# usage: rebuild-db.sh [database]

set -xeo pipefail

if [[ -z "$1" ]]; then
  echo "no argument provided; defaulting to cc-testing"
  db="cc-testing"
else
  db=$1
fi

if [[ "$db" != "cc-testing" ]] && \
   [[ "$db" != "cc-dev" ]] && \
   [[ "$db" != "cc-staging" ]] && \
   [[ "$db" != "cc-test" ]]
then
  echo "$db" is not a database that this script knows about. Are you sure you want to drop this database? [Y/n]
  read  -n 1 -p "$1 is not a database that this script knows about. Are you sure you want to drop this database? [Y/n]" confirmation
  if [[ "$confirmation" = "N" ]] || [[ "$confirmation" = "n" ]]; then
    echo doing nothing and exiting...
    exit 0
  fi
fi

dropdb --host=localhost --user=arco --if-exists $db
createdb --host=localhost --user=arco -O arco $db

#!/usr/bin/env bash

dropdb --if-exists cc-staging
dropuser arco
createuser --pwprompt arco
createdb -O arco cc-staging

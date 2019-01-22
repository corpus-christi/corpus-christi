#!/usr/bin/env bash

if [[ ! $PWD =~ 'Corpus Christi'$ ]]
then
    echo Must run at top-level of source tree.
    exit 1
fi

wc $(for path in ui/src api/src
do
    find $path -type f -print
done | egrep -v '__pycache__|\.json$|\.DS_Store') | sort -n

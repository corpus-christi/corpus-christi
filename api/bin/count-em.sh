#!/usr/bin/env bash

if [[ ! $PWD =~ 'corpus-christi'$ ]]
then
    echo Must run at top-level of source tree.
    exit 1
fi

wc $(for path in ui/src api/src
do
    find $path -type f -print | sort
done | egrep -v '__pycache__|\.json$|\.DS_Store')

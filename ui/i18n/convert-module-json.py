#!/usr/bin/env python

"""
Bring module-specific data into conformance with existing L10N.
"""

import json
import sys

import yaml

global_file_count = 0
global_entry_count = 0

file_name = sys.argv[1]
top_level_name = sys.argv[2]

with open(file_name) as in_file:
    in_data = json.load(in_file)

    dd = {}
    for datum in in_data:
        ld = {}
        dd[datum["code"]] = ld
        for locale in datum['locales']:
            ld[locale["locale_code"]] = locale["name"]
    print(yaml.dump({top_level_name: dd}))

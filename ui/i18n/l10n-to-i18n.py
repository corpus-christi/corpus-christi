#!/usr/bin/env python3

"""
Convert i10n maps to a vue-i18n map.
"""

import json
import sys
from contextlib import redirect_stdout

import yaml

global_file_count = 0
global_entry_count = 0


def read_yaml(file_name):
    data = None
    with open(file_name, "r") as f:
        data = yaml.load(f)
    return data


def convert_to_vue_i18n_map(i10n_map, vue_i18n_map={}):
    """Convert l10n map to vue-i18n map.

    If vue_i18n is not None, combine new entries with existing map.
    """
    intermediate = []

    def convert_to_list_helper(word_map, dot_path=[]):
        """Convert l10n map to list of objects containing a key path and the gloss."""
        global global_entry_count
        for (key, val) in word_map.items():
            if isinstance(val, dict):
                convert_to_list_helper(val, dot_path + [key])
            else:
                if not key.startswith('_'):
                    intermediate.append({
                        'path': [key] + dot_path,
                        'gloss': val
                    })
                    global_entry_count += 1

    convert_to_list_helper(i10n_map)

    # Now traverse the key path arrays and create a new nested dictionary suitable for vue-i18n.
    for entry in intermediate:
        d = vue_i18n_map
        but_last, last = entry['path'][:-1], entry['path'][-1]
        for key in but_last:
            if key not in d:
                d[key] = {}
            d = d[key]
        if last in d:
            raise RuntimeError(f"{entry['path']} already '{d[last]}', won't set to '{entry['gloss']}'")
        d[last] = entry['gloss']

    return vue_i18n_map


final_map = {}
for file_name in sys.argv[1:]:
    global_file_count += 1
    map_in = read_yaml(file_name)
    # pprint(map_in)
    # print("-" * 40)
    map_out = convert_to_vue_i18n_map(map_in, final_map)
    # pprint(map_out)
    # print("-" * 40)

print(json.dumps(final_map, indent=2, sort_keys=True))

with redirect_stdout(sys.stderr):
    print(f"Languages: {list(final_map.keys())}")
    print(f"    Files: {global_file_count}")
    print(f"  Entries: {global_entry_count}")

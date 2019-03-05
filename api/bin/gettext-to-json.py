#!/usr/bin/env python3

import sys

with open(sys.argv[1], 'r') as fp:
    for line in fp:
        line = line.strip()
        line = line.replace('#~ ', '')
        if line.startswith('msgid'):
            print('{')
            print('"id": "",')
            print('"desc": "",')
            line = line.replace('msgid ', '')
            print(f'"en": {line},',)
        elif line.startswith('msgstr'):
            line = line.replace('msgstr ', '')
            print(f'"es": {line}')
            print('},')
fp.close()

#!/usr/bin/env python3
""" An interactive tool to complete the translation of one locale based on the glossory listed in another locale 
python dependencies: ruamel.yaml, googletrans (if using auto translate)
"""
# known issue:  <2020-06-24, David Deng> #
# ruamel.yaml currently uses yaml 1.2 spec, whereas pyyaml uses 1.1 spec.
#   A problem caused by this is that the string key 'NO' in yaml/country-l10n.yaml needs quotes around it in 1.1 version
#   whereas ruamel.yaml will generate unquoted key, which will be interpreted as a boolean under the 1.1 version

import sys
import os
import time
import itertools
import collections
from ruamel.yaml import YAML # preserving order and comments in the original yaml file

yaml = YAML()

if len(sys.argv) <= 1:
    print("Usage: python3 {sys.argv[0]} xx-l10n.yaml [...]")
    sys.exit()
infiles = sys.argv[1:] or []

### helpers
def get_list_items(word_map, dot_path=[]):
    """Convert l10n map to an iterable of objects containing a key path and locales
    according to the original key structure."""
    if not isinstance(word_map, collections.Mapping):
        raise Exception(f"Can't get items from non-mapping object {word_map}")
    if all([isinstance(val, str) for val in word_map.values()]):
        return [{
            'path': dot_path,
            'locales': { key: val for key, val in word_map.items()
                if not key.startswith("_")}
            }]

    # combine list items returned from the children dictionaries
    # assume all values in word_map are dictionaries, otherwise, they are ignored
    return itertools.chain(*[get_list_items(val, dot_path + [key]) 
        for key, val in word_map.items() 
        if isinstance(val, collections.Mapping)])

def read_yaml(filename):
    with open(filename, "r") as f:
        data = yaml.load(f)
    return data

def get_input(message, validator=lambda a:True, error_feedback="Invalid input, please try again", default=False):
    if default:
        message += f"\n({default}) => "
    else:
        message += "\n=> "
    user_input = input(message)
    while (user_input or not default) and not validator(user_input):
        # validate when input is not empty, or when default is not set
        print(error_feedback)
        user_input = input(message)
    if not user_input:
        print(f"Using default value: ({default})")
    return user_input or default

def get_nested_dict_item(dictionary, path):
    if not path:
        return dictionary
    return get_nested_dict_item(dictionary[path[0]], path[1:])

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

### main logic
def main():
    # configure auto translate
    auto_translate = get_input("Do you want the program to auto-translate phrases using googletrans? (y/n)",
            lambda confirm:confirm in ['y','n'],
            default='y'
            ) == 'y'
    if auto_translate:
        import googletrans
        t = googletrans.Translator()

    # configure locales
    default_locale_src = "en-US"
    locale_src = get_input(
            f"Enter the source locale to translate from, leave empty to use the default ({default_locale_src})"\
                    "\nNote: The source locale must be present in the yaml files in order for completion to take place.", 
            lambda locale: locale != "",
            error_feedback="The source locale cannot be empty. Example locales: en-US, es-EC, zh-CN",
            default=default_locale_src)

    default_locale_dest = "es-EC"
    locale_dest = get_input("Enter the destination locale to be completed",
            lambda locale: locale != "",
            error_feedback="The destination locale cannot be empty",
            default=default_locale_dest)

    # configure languages
    if auto_translate:
        lang_map = googletrans.LANGUAGES

        default_lang_src = next((lang for lang in lang_map.keys() if lang[:2].lower() == locale_src[:2].lower()), "en")
        default_lang_dest = next((lang for lang in lang_map.keys() if lang[:2].lower() == locale_dest[:2].lower()), "es")

        lang_src = get_input(
                "Enter the source language, leave empty to use the default",
                validator=lambda lang: lang in lang_map,
                error_feedback=f"Invalid language, possible languages: {', '.join(lang_map.keys())}",
                default=default_lang_src)

        lang_dest = get_input(
                "Enter the destination language, leave empty to use the default",
                validator=lambda lang: lang in lang_map,
                error_feedback=f"Invalid language, possible languages: {', '.join(lang_map.keys())}",
                default=default_lang_dest)

    # configure other variables
    always_overwrite = False
    auto_pass = False
    auto_pass_timer = None # prevent being blocked by the server

    # go through the files
    for idx, infile in enumerate(infiles, 1):
        print(f"Processing file ({idx}/{len(infiles)}): {infile}")
        l10n_map = read_yaml(infile)
        list_items = list(get_list_items(l10n_map))

        # get all locales
        locale_set = set()
        for item in list_items:
            locale_set.update(item['locales'].keys())
        locale_list = list(locale_set)

        if not locale_list:
            print("No locale detected, skipping")
            continue
        elif locale_src not in locale_list:
            print("Source locale {locale_src} not detected, skipping")
            continue

        print(f"Locales detected in {infile}: {locale_list}")


        # modify list_items
        completed_item_count = 0
        for list_item in list_items:
            if (locale_src in list_item['locales']
                    and locale_dest not in list_item['locales']):
                translation_source = list_item['locales'][locale_src]
                translation_result = t.translate(
                        translation_source,
                        src=lang_src, 
                        dest=lang_dest).text if auto_translate else ""
                print(f"{'.'.join(list_item['path'])} is absent from {locale_dest}")
                print(f"add translation [{translation_source}] => [{translation_result}]?")

                if auto_pass:
                    confirm = 'y'
                    time.sleep(auto_pass_timer)
                else:
                    options = { 'y': 'Yes, use the current translation' ,
                            'n': 'No, skip this entry',
                            'e': 'Edit the current entry',
                            'a': 'Automatically use the rest of the translation without asking',
                            'q': 'Quit the program' }
                    confirm = get_input("\n".join([ f"[{key}]: {val}" for key, val in options.items() ]), 
                            lambda confirm: confirm in options.keys())

                if confirm == 'e':
                    translation_result = get_input("Enter a new translation to override the default one",
                            default=translation_result)
                    confirm = 'y'

                if confirm == 'a':
                    auto_pass = True
                    if auto_pass_timer is None: # set timer on the first time
                        if auto_translate:
                            auto_pass_timer = float(get_input(
                                    "Do you want a pause between each iteration to avoid overly frequent request?"\
                                    "\nEnter the amount of seconds to pause",
                                    is_float,
                                    default = 0.3))
                        else:
                            auto_pass_timer = 0
                    confirm = 'y'

                if confirm == 'y':
                    item = get_nested_dict_item(l10n_map, list_item['path'])
                    item[locale_dest] = translation_result
                    completed_item_count += 1
                    print(f"Entry [{translation_result}] added")
                elif confirm == 'n':
                    print(f"Entry [{translation_result}] not added.")
                    continue
                elif confirm == 'q':
                    print("Nothing changed.")
                    sys.exit()
                else:
                    raise Exception(f"Invalid input for confirmation: {confirm}")

        print(f"Completed items: {completed_item_count}")

        if completed_item_count > 0:
            options = { 'y': 'Yes, overwrite and create a backup file' ,
                    'n': 'No, only print the result in standard output',
                    'a': 'Overwrite for all future files processed' }
            print(f"Overwrite the existing file [{infile}] and create a backup file [{infile}.bak]?")

            overwrite = 'y' if always_overwrite else get_input("\n".join([ f"[{key}]: {val}" for key, val in options.items() ]), 
                    lambda overwrite: overwrite in options.keys(),
                    default='y')

            if overwrite == 'a':
                always_overwrite = True
                overwrite = 'y'

            if overwrite == 'y':
                os.rename(infile, f"{infile}.bak")
                print(f"Successfully created backup file [{infile}.bak]")
                with open(infile, "w") as f:
                    yaml.dump(l10n_map, f)
                print(f"New content written into [{infile}]")
            else:
                print("Original file not changed, new content listed below")
                print("-"*50)
                yaml.dump(l10n_map, sys.stdout)
                print("-"*50)

main()

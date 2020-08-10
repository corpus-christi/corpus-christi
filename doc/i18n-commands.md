# i18n Command Suites

This document contains some detailed explanation
about the `flask i18n` commands.

The main purpose of the `flask i18n` commands is
to allow developers to maintain translation
entries effectively.

## Convention and Definition

For brevity purpose, when referring to command
names in this document, a prefix `flask i18n` is
assumed. For example, `add` refers to the command
`flask i18n add`.

In this document, an _entry_ is used as a synonym
for a record in the `I18NValue` table.

## Available Commands

This section seeks to highlight the features of
and philosophy behind some of the available
commands.

For information related to command arguments,
options, or example usage, see: 
`flask i18n <command> --help`

Below is a list of available `<command>`s for
reference. 

- `add` Add an entry into the database.
- `delete` Delete entries from the database.
- `dump` Dump entries from the database into a
  json file.
- `dump-descriptions` Dump descriptions into a
  json file from the database.
- `edit` Interactively edit entries.
- `export` Export entries into a yaml file.
- `import` Import entries from a yaml file.
- `list` Print entries in the yaml format.
- `load` Load entries from a json file into the
  database.
- `load-descriptions` Load descriptions from a
  json file into the database.
- `translate` Translate entries in the database.
- `update` Update an entry in the database.

### Extract database entries: `dump` v.s. `export`

Both the `dump` and `export` commands accomplish a
job of extracting entries from the database into a
file. However, their intended usages are rather
different.

While the main job of `dump` is to _persist
complete information_ from the database, the
`export` command aims at providing a
_developer-friendly_ output for viewing and
editing each entry gloss. 

For example, the output of the `dump` command
contains the "verified" flag in order to keep
track of the verification status of each entry in
the revision control; on the other hand, the
output of the `export` command does not include
the "verified" flag, since it is mostly irrelevant
to a developer who mainly wants to view the
content of the entry.

As a result, the output of `dump` is meant to be
tracked with the revision control, while that of
`export` is not. For this reason, the destination
of `dump` automatically defaults to
`corpus-christi/api/i18n/<locale>.json`, where
`<locale>` is the given locale code in the form of
`ab-XY`.

Another main difference between the two is their
output format. The `dump` command exports entries
on a one-file-per-locale basis with the JSON
format, while the `export` command arranges
entries in a [locale-tail structured
tree](#locale-tail-structure) with the YAML
format.

Their parameters are also slightly different.
While `dump` requires a `<locale>` to be provided,
`export` always outputs all locales. On the other
hand, `export` accepts an optional "PATH"
parameter to allow an arbitrary "zoom-in" on
certain groups of entries, the `dump` command
always outputs the whole structure.

A counterpart of `dump` is `load`, which does the
opposite of `dump` by loading entries listed in a
file into the database. Similarly, the counterpart
of `export` is `import`.

### Utilities surrounding `dump` and `load`

Since each `I18NKey` also have a single (nullable)
"description" field, on the data level, the
"description" can simply be represented as another
locale. Description data is often labeled with a
pseudo locale code `_desc` to prevent naming
conflict with any valid locale codes.

To extract descriptions from the database, use the
`dump-descriptions` command, which by default
extracts the descriptions into the file
`corpus-christi/api/i18n/_desc.json`. The
`load-descriptions` command does the opposite by
modifying descriptions in the database with
description data contained in a file.

### Utilities surrounding `export` and `import`

A number of other commands are simply "syntactic
sugar" for the `import` and `export` commands, in
the sense that they perform actions that can be
accomplished by `export` and `import` with less
complicated and esoteric syntax.

Those commands and their `export`, `import`
equivalent are listed below:

#### `list`

Sample command

```bash
flask i18n list
```

Equivalent with `export`

```bash
flask i18n export --target -
```

Note the `-` provided to the option `--target`
sets up the command to take input from stdin or
redirect output to stdout.

#### `update`

Sample command

```bash
flask i18n update en-US actions.activate-account "Activate Account"
```

Equivalent with `import`

```bash
flask i18n import --target - --override actions.activate-account <<< "en-US: Activate Account"
```

The `<<<` syntax specifies a [Here
String](https://www.tldp.org/LDP/abs/html/x17837.html)
that will be used as standard input, and like the
previous example, the input file is set to stdin
with the `-` value provided to the `--target`
option.

One difference in this example is that `update`
will prevent the action if the value with key
"actions.activate-account" and locale "en-US" does
not already exist in the database, while `import`
will not.

#### `add`
Sample command

```bash
flask i18n add en-US actions.activate-account "Activate Account"
```

Equivalent with `import`

```bash
flask i18n import --target - --no-override actions.activate-account <<< "en-US: Activate Account"
```

#### `edit`

The `edit` command is an interactive, and a more
elaborate form of syntactic sugar on both `export`
and `import`, which provides a greater degree of
convenience and efficiency than the previously
listed commands.

Sample command

```bash
flask i18n edit actions.activate-account
```

Equivalent with `export` and `import`

```bash
flask i18n export --target RANDOM.yaml actions.activate-account
# edit RANDOM.yaml with a text editor
flask i18n import --target RANDOM.yaml --override actions.activate-account
rm RANDOM.yaml
```

where `RANDOM.yaml` is a random file name with no
naming conflict with existing files.

An editor will be launched upon the execution of
the `edit` command. In Unix-like systems, the
choice of text editor will respect the `EDITOR`
environment variable.

Upon saving the file and closing the editor,
entries will be automatically updated in the
database. If the given file contains error, the
file will be saved to a temporary location with a
friendly prompt to reedit the file and `import`
again into the database after errors are removed.

If the editor is closed without saving, the
database will not be changed.

### Remove entries from the database: `delete`

Although some commands mentioned above are by
default, or can be, configured to "override"
entries that already exist, none of them will
_remove_ any existing entries from the database.

The removal of entries can be done with the
`delete` command. For usage information, see
`flask i18n delete --help`.

### Automatically translate entries: `translate`

When some new keys are added into the application
UI, it can be tedious for developers to copy-paste
translations from a browser window (likely with
google translate open).

The `translate` command aims at simplfiying this
process by utilizing the [googletrans](https://pypi.org/project/googletrans/) library and
automatically completing entries from one language
to another.

General usage information is described in
`flask i18n translate --help`.

Since the translation of each entry is
accomplished by making a request to a remote
server, it is possible that the server produces
undesired behaviors with overly frequent requests
(e.g. incorrect result being returned, IP
addressed blocked by the server, etc.). To prevent
this from happening, the command has a
`--delay-timer` option which accepts a (floating
point) number of seconds to be delayed in between
each request. The default is set to 0.3, and under
most circumstances, this should be provide a good
balance between speed and stability.

`googletrans` uses a similar, but different set of
two-letter language codes from the locale code
used by CC. The `translate` command will attempt
to deduce the language by matching the first two
letters of the locale code to any available
language code. If this fails, or if some other
source/destination language is desired to be used,
one can use the `--src-lang` and `--dest-lang`
options to override the auto-detected languages.

A list of available language codes will be
displayed if 

1. the specified language code is invalid, or
1. the command cannot deduce the language code
   from the given locale code.
    
## Common options

### Target

Many commands takes a `--target` option, which
always refers to the name of the file on which the
command is operating on. When `--target` is `-`,
the file will be stdin/stdout.

### Verbose 

Most commands that alter database information have
a `--verbose` flag which is set to True by
default. This will make the command print out the
entries being modified as it processes the
entries. To disable verbose output, use the
`--silent` or `-s` flag.

## Locale-Tail structure

A locale-tail-structured tree is a tree where
each end entry contains its corresponding gloss
value in different locales, as opposed to a
"locale-head" tree, where entry gloss themselves
are first categorized according to their locales.

Below is a sample locale-tail-structured tree
expressed in the YAML format, which is similar to
the structure used by the `export` command:

    actions:
      tooltips:
        activate:
          en-US: Activate
          es-EC: Activar
        archive:
          en-US: Archive
          es-EC: Archivar

The same information can also be expressed in the
"locale-head" structure, which is similar to that
used by the `dump` command:

    en-US:
      actions:
        tooltips:
          activate: Activate
          archive: Archive
    es-EC:
      actions:
        tooltips:
          activate: Activar
          archive: Archivar

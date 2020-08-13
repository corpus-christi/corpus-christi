import json
import yaml
import click
import re
import os
import sys
import tempfile
import googletrans
import sqlalchemy
import time

from flask.cli import AppGroup
from src import BASE_DIR, db
from src.i18n.models import I18NLocale, I18NKey, I18NValue
from src.shared.helpers import (
    tree_to_list,
    list_to_tree,
    BadTreeStructure,
    BadListKeyPath,
    get_or_create)


# --- exceptions

class ExceptionHandlingCommand(click.Command):
    """ A custom subclass to handle common exceptions raised in i18n commands """

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except yaml.YAMLError as e:
            click.echo("\nError: An error occurred when processing yaml file")
            click.echo(f"Error message: {e}")
            exit(1)
        except json.JSONDecodeError as e:
            click.echo("\nError: An error occurred when decoding json file")
            click.echo(f"Error message: {e}")
            exit(1)
        except BadListKeyPath as e:
            click.echo("\nError: A bad i18n key path is encountered")
            click.echo(f"Error message: {e}")
            exit(1)
        except BadTreeStructure as e:
            click.echo(
                "\nError: An invalid locale-tail structured tree is encountered")
            click.echo(f"Error message: {e}")
            exit(1)

# --- helpers


def is_valid_locale_code(locale_code):
    return re.fullmatch('[a-z]{2}-[A-Z]{2}', locale_code)


def validate_locale(ctx, param, value):
    """ a command option callback to make sure that the given string is a valid locale """
    if not is_valid_locale_code(value):
        raise click.BadParameter(
            f"{value} is not a valid locale code. It must be in the form of ab-XY")
    return value


def validate_locale_allow_none(ctx, param, value):
    """ a command option callback to make sure that
    the given string is either None or a valid locale
    """
    if value is not None:
        return validate_locale(ctx, param, value)
    else:
        return value


def get_formatted_language_map():
    formatter = "{:10}| {:10}"
    divider = "-" * 25
    title = "All available language codes:\n"

    return "\n".join(
        [
            title,
            formatter.format("code", "description"),
            divider
        ] +
        [
            formatter.format(code, desc)
            for code, desc in googletrans.LANGUAGES.items()
        ])


def is_valid_language_code(language_code):
    return language_code in googletrans.LANGUAGES


def validate_language(ctx, param, value):
    """ validate whether the given language is valid,
    list all possible languages if an invalid one is given
    """
    if not is_valid_language_code(value):
        raise click.BadParameter(
            f"{value} is not a valid language code.\n\n" +
            get_formatted_language_map()
        )
    return value


def validate_language_allow_none(ctx, param, value):
    """ validate whether the given language is valid or None """
    if value is not None:
        return validate_language(ctx, param, value)
    else:
        return value


def sanitize_path(ctx, param, value):
    """ remove leading/trailing dots on a path if there are any
    can be modified to do additional sanitizations
    """
    return value.strip('.')


def create_dir(ctx, param, value):
    """ a command option callback to create parent directories if does not exist """
    pardir = os.path.dirname(value.name) if hasattr(value, 'name') else None
    if pardir:
        os.makedirs(pardir, exist_ok=True)
    return value


def default_target():
    """ resolve the default target for dump/load commands based on the
    user-specified <locale> parameter
    """
    params = click.get_current_context().params
    if 'locale' not in params:
        click.echo(
            "Can't get default target from the specified <locale> parameter")
        raise click.Abort()
    locale = params['locale']
    return os.path.join(BASE_DIR, 'i18n', f"{locale}.json")


def read_locale_tail_tree(parent_path=""):
    """read from the database entries starting with parent_path
    returns a valid "locale-tail" tree if possible.

    a "locale-tail" tree is a tree where each end entry contains
    its corresponding gloss in different locales, as opposed to
    a "locale-head" tree, where entry gloss themselves are
    categorized according to the locales.

    If it is impossible to create a valid tree, raise a BadListKeyPath error

    :parent_path: the base dotted path, entries not starting with
    this path will be ignored. parent_path must be a complete path segment
    leading and trailing '.'s will be stripped
    In the actual tree, the parent_path will be omitted.

    :returns: If parent_path is a valid key in the database, a single object
    with all locales on that key is returned
    otherwise, a valid locale-tail tree of all nodes containing parent_path
    is returned.
    If there is no matching entries, None is returned
    """
    def key_to_list_item(key, strip_key=None):
        """ list_item: { 'path': 'a.b.x', 'value': node } """
        list_item = {
            'path': key.id,
            'value': {
                value.locale_code: value.gloss for value in key.values
            }}
        if strip_key:
            if list_item['path'].startswith(strip_key):
                list_item['path'] = list_item['path'][len(
                    strip_key):].lstrip('.')
            else:
                raise BadListKeyPath(
                    f"Unexpected strip_key: [{list_item['path']}] does not start with [{strip_key}]")
        if key.desc:
            list_item['value']['_desc'] = key.desc
        return list_item

    # if found an exact match, return that entry
    key = db.session.query(I18NKey).filter_by(id=parent_path).first()
    if key:
        return key_to_list_item(key)['value']

    # otherwise, find all sub-entries and build a tree
    query = db.session.query(I18NKey)
    if parent_path:
        query = query.filter(I18NKey.id.like(f'{parent_path}.%'))
    all_keys = query.all()
    if all_keys:
        lst = [key_to_list_item(key, strip_key=parent_path)
               for key in all_keys]
        return list_to_tree(lst)
    else:
        return None


def write_locale_tail_tree(tree, parent_path="", override=True, verbose=False):
    """Reverse the process of read_locale_tail_tree,
    write the given tree into the database.

    :tree: the tree to be written into the database.
    A leaf is a tree that resenbles the following structure:
    { 'ab-XY': string, '_desc': string }
    If the 'tree' is a leaf, then the given locale-specific values
    gloss are directly written into the entry with key_id equal to 'parent_path'
    If the 'tree' is not a leaf, each of its branches must terminate with
    a leaf. And each leaf is written into the entry with key_id
    equal to a dot-separated string with all labels along its branch.

    :parent_path: the path to which to append the tree

    :override: whether to override existing values in the database.
    if True, the 'verified' flag will be set to False after the update

    :returns: a result object:
    { entry_count: int, skip_count: int }

    an BadTreeStructure will be raised if the given input contains
    an invalid tree structure

    """
    entry_count, skip_count = 0, 0

    def is_leaf(node):
        return isinstance(node, dict) \
            and all([(key == '_desc' or is_valid_locale_code(key))
                     and isinstance(val, str) for key, val in node.items()])
    # if the given tree is a leaf
    if is_leaf(tree):
        # override the item specified by parent_path
        if not parent_path:
            raise click.BadParameter(
                f"Must specify a path when overriding with a leaf node {tree}")
        # make sure parent_path is not an intermediate path
        child = db.session.query(I18NKey).filter(
            I18NKey.id.like(f'{parent_path}.%')).first()
        if child:
            raise BadTreeStructure(
                f"[{parent_path}] is an intermediate path with child [{child.id}], "
                "cannot update with a leaf node")
        # construct a single item to be written
        lst = [{'path': [], 'value': tree}]
    # otherwise, flatten the given tree
    else:
        # make sure parent_path is not an entry
        if parent_path and db.session.query(
                I18NKey).filter_by(id=parent_path).count():
            raise BadTreeStructure(
                f"[{parent_path}] is already an entry, cannot write sub-entries onto that")

        lst = tree_to_list(tree, is_leaf)
    for item in lst:
        key_list = item['path']
        if parent_path:
            key_list.insert(0, parent_path)
        key_id = '.'.join(key_list)
        key = get_or_create(db.session, I18NKey, {'id': key_id})
        existing_values = {value.locale_code: value for value in key.values}
        for locale_code, gloss in item['value'].items():
            if locale_code == '_desc':
                # process description
                if key.desc and not override:
                    skip_count += 1
                    continue
                else:
                    key.desc = gloss
                    if verbose:
                        click.echo(
                            f"overriding [{key_id}]'s description with [{gloss}]")
            else:
                # process key value linked to the locale
                if locale_code in existing_values:
                    if not override:
                        skip_count += 1
                        continue
                    else:
                        existing_values[locale_code].gloss = gloss
                        existing_values[locale_code].verified = False
                        if verbose:
                            click.echo(
                                f"overriding [{key_id}] in [{locale_code}] with [{gloss}]")
                else:
                    locale = get_or_create(
                        db.session, I18NLocale, {'code': locale_code})
                    value = I18NValue(
                        gloss=gloss,
                        verified=False,
                        key_id=key_id,
                        locale_code=locale_code
                    )
                    key.values.append(value)
                    if verbose:
                        click.echo(
                            f"adding [{key_id}] in [{locale_code}] with [{gloss}]")
            entry_count += 1
        db.session.add(key)
    db.session.commit()
    return {'entry_count': entry_count, 'skip_count': skip_count}

# --- commands


def create_i18n_cli(app):
    i18n_cli = AppGroup('i18n', help="Maintain translation entries.")
    app.cli.add_command(i18n_cli)

# --- flask i18n load

    @i18n_cli.command('load', cls=ExceptionHandlingCommand)
    @click.argument('locale', callback=validate_locale, metavar="<locale>")
    @click.option('--override/--no-override', default=True,
                  show_default=True,
                  help="Override if value already exists")
    @click.option('--target',
                  default=default_target,
                  show_default=os.path.join(BASE_DIR, 'i18n', "<locale>.json"),
                  type=click.File("r"),
                  help="The source file to load values from")
    @click.option('-v/-s',
                  '--verbose/--silent',
                  is_flag=True,
                  default=True,
                  show_default=True,
                  help="Print output as modifying the database")
    def load_values(locale, target, override, verbose):
        """ Load entries from a json file into the database.

        <locale>: the locale code of the processed values. E.g. en-US

        Example usage:

        \b
            flask i18n load en-US

        \b
            flask i18n load --target en-US.json en-US
        """
        entry_count = 0
        skip_count = 0
        locale_name = locale
        click.echo(
            f"loading values from [{getattr(target, 'name', '(unknown stream)')}]")
        tree = json.load(target)

        def is_leaf(node):
            return isinstance(node, dict) \
                and 'gloss' in node \
                and isinstance(node['gloss'], str)

        entries = tree_to_list(tree, is_leaf=is_leaf)
        locale = get_or_create(db.session, I18NLocale, {'code': locale_name})
        for entry in entries:
            key_id = '.'.join(entry['path'])
            key = get_or_create(db.session, I18NKey, {'id': key_id})
            value = db.session.query(I18NValue).filter_by(
                key_id=key.id, locale_code=locale.code).first()
            if value:
                if override:
                    value.gloss = entry['value']['gloss']
                    value.verified = entry['value']['verified']
                else:
                    skip_count += 1
                    continue
            else:
                value = I18NValue(
                    gloss=entry['value']['gloss'],
                    verified=entry['value']['verified'],
                    key_id=key.id,
                    locale_code=locale.code
                )
            db.session.add(value)
            entry_count += 1
            if verbose:
                click.echo(f"adding I18NValue [{key_id}: {entry['value']}]")
        db.session.commit()
        click.echo("Successfully loaded data into the database")
        click.echo(
            f"Source file: {getattr(target, 'name', '(unknown stream)')}")
        click.echo(f"Locale:      {locale_name}")
        click.echo(f"Entry count: {entry_count}")
        click.echo(f"Skip count:  {skip_count}")

# --- flask i18n dump

    @i18n_cli.command('dump', cls=ExceptionHandlingCommand)
    @click.argument('locale', callback=validate_locale, metavar="<locale>")
    @click.option('--target',
                  default=default_target,
                  show_default=os.path.join(BASE_DIR, 'i18n', "<locale>.json"),
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to dump values to")
    def dump_values(locale, target):
        """ Dump entries from the database into a json file.

        <locale>: the locale code of the processed values. E.g. en-US

        Example usage:

        \b
            flask i18n dump en-US

        \b
            flask i18n dump --target en-US.json en-US
        """

        click.echo(
            f"dumping values into {getattr(target, 'name', '(unknown stream)')}")
        values = db.session.query(I18NValue).filter_by(
            locale_code=locale).all()
        entries = map(
            lambda value: {
                'path': value.key_id,
                'value': {
                    'gloss': value.gloss,
                    'verified': value.verified
                }
            }, values)
        tree = list_to_tree(entries)
        json.dump(tree, target, indent=2, sort_keys=True)
        click.echo("Successfully dumped data from the database")
        click.echo(
            f"Target file: {getattr(target, 'name', '(unknown stream)')}")
        click.echo(f"Locale:      {locale}")
        click.echo(f"Entry count: {len(values)}")

# --- flask i18n load-descriptions

    @i18n_cli.command('load-descriptions', cls=ExceptionHandlingCommand)
    @click.option('--override/--no-override',
                  default=False,
                  show_default=True,
                  help="Override if descriptions is non-empty")
    @click.option('--target',
                  default=os.path.join(BASE_DIR, 'i18n', "_desc.json"),
                  show_default=True,
                  type=click.File("r"),
                  help="The source file to load descriptions from")
    @click.option('-v/-s',
                  '--verbose/--silent',
                  is_flag=True,
                  default=True,
                  show_default=True,
                  help="Print output as modifying the database")
    def load_descriptions(target, override, verbose):
        """ Load descriptions from a json file into the database.

        Example usage:

        \b
            flask i18n load-descriptions

        \b
            flask i18n load-descriptions --override --target desc.json
        """
        entry_count = 0
        skip_count = 0
        tree = json.load(target)
        entries = tree_to_list(tree)
        click.echo(
            f"loading descriptions from [{getattr(target, 'name', '(unknown stream)')}]")
        for entry in entries:
            key_id = '.'.join(entry['path'])
            key = db.session.query(I18NKey).filter_by(id=key_id).first()
            description = entry['value']
            if not key:
                if verbose:
                    click.echo(
                        f"key [{key_id}] does not exist in database, creating one with description [{description}]")
                key = I18NKey(
                    id=key_id,
                    desc=description)
            elif key.desc and not override:  # if description non-empty and not overriding
                if verbose:
                    click.echo(
                        f"key [{key_id}] already has description [{key.desc}], not overriding with [{description}]")
                skip_count += 1
                continue
            else:
                if verbose:
                    click.echo(
                        f"overriding description of key [{key_id}] [{key.desc}] with [{description}]")
                key.desc = description
            db.session.add(key)
            entry_count += 1
        db.session.commit()
        click.echo("Successfully loaded descriptions into the database")
        click.echo(
            f"Source file: {getattr(target, 'name', '(unknown stream)')}")
        click.echo(f"Entry count: {entry_count}")
        click.echo(f"Skip count:  {skip_count}")
        if skip_count:
            click.echo(
                "Hint: use --override to load descriptions even if they exist")

# --- flask i18n dump-descriptions

    @i18n_cli.command('dump-descriptions', cls=ExceptionHandlingCommand)
    @click.option(
        '--dump-empty/--no-dump-empty',
        default=False,
        show_default=True,
        help="Dump description even if it is empty "
        "(can be useful when want to retrieve a complete list of keys)")
    @click.option(
        '--empty-placeholder',
        default="",
        show_default=True,
        help="The description to use when the description in database is not given or empty, "
        "must be used with --dump-empty to take effect")
    @click.option('--target',
                  default=os.path.join(BASE_DIR, 'i18n', "_desc.json"),
                  show_default=True,
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to dump descriptions to")
    def dump_descriptions(target, dump_empty, empty_placeholder):
        """ Dump descriptions into a json file from the database.

        Example usage:

        \b
            flask i18n dump-descriptions

        \b
            flask i18n dump-descriptions --target desc.json \\
                --dump-empty --empty-placeholder "No description"
        """
        query = db.session.query(I18NKey)
        if not dump_empty:
            query = query.filter(
                I18NKey.desc is not None).filter(
                I18NKey.desc != "")
        keys = query.all()

        entries = map(
            lambda key: {
                'path': key.id,
                'value': key.desc or empty_placeholder
            }, keys)
        tree = list_to_tree(entries)
        json.dump(tree, target, indent=2, sort_keys=True)
        click.echo("Successfully dumped data from the database")
        click.echo(
            f"Target file: {getattr(target, 'name', '(unknown stream)')}")
        click.echo(f"Entry count: {len(keys)}")

# --- flask i18n export

    @i18n_cli.command('export', cls=ExceptionHandlingCommand)
    @click.argument('path', callback=sanitize_path, default="")
    @click.option('--target',
                  required=True,
                  show_default=True,
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to export the tree to")
    def export_entries(path, target):
        """ Export entries into a yaml file.

        List all entries that start with PATH in a 'locale-tail' structured tree

        Specify the destination file with --target

        Example usage:

        \b
            flask i18n export --target country-names.yaml country.name
        """
        tree = read_locale_tail_tree(path)
        if tree:
            yaml.dump(tree, target, default_flow_style=False, sort_keys=True)
        else:
            click.echo(f"No entries found")

# --- flask i18n list

    @i18n_cli.command('list', cls=ExceptionHandlingCommand)
    @click.argument('path', callback=sanitize_path, default="")
    @click.pass_context
    def list_entries(ctx, path):
        """ Print entries in the yaml format.

        this command does the same thing as 'flask i18n export', except --target is set to sys.stdout

        Example usage:

        \b
            flask i18n list

        \b
            flask i18n list country.name
        """
        ctx.invoke(export_entries, path=path, target=sys.stdout)


# --- flask i18n import

    @i18n_cli.command('import', cls=ExceptionHandlingCommand)
    @click.argument('path', callback=sanitize_path, default="")
    @click.option('--target',
                  default='-',
                  show_default=True,
                  type=click.File("r"),
                  help="The source file to load data into the database")
    @click.option('--override/--no-override', default=True,
                  show_default=True,
                  help="Override if value already exists. "
                  "If true, then for values that are overridden, "
                  "the corresponding 'verified' flag will be set to False.")
    @click.option('-v/-s',
                  '--verbose/--silent',
                  is_flag=True,
                  default=True,
                  show_default=True,
                  help="Print output as modifying the database")
    def import_entries(path, target, override, verbose):
        """ Import entries from a yaml file.

        Load all entries expressed in a 'locale-tail' structured tree into the database,
        prepend each entry's path with PATH

        PATH is optional when the yaml file is not a single entry,

        Example usage:

        \b
            flask i18n import --target country-names.yaml country.name

        \b
            flask i18n import --target - country.name.US << HEREDOC
            en-US: United States
            es-EC: Estados Unidos
            HEREDOC
        """
        tree = yaml.safe_load(target)
        result = write_locale_tail_tree(tree, path, override, verbose)
        click.echo("Successfully loaded data into the database")
        click.echo(
            f"Source file: {getattr(target, 'name', '(unknown stream)')}")
        click.echo(f"Entry count: {result['entry_count']}")
        click.echo(f"Skip count:  {result['skip_count']}")


# --- flask i18n add

    @i18n_cli.command('add')
    @click.argument('locale', callback=validate_locale)
    @click.argument('path')
    @click.argument('gloss')
    def add_entry(locale, path, gloss):
        """ Add an entry into the database.

        Example usage:

        \b
            flask i18n add en-US actions.activate-account "Activate Account"

        No override will occur if the given entry already exists

        To update entry, use the 'update' command
        """
        value = db.session.query(I18NValue).filter_by(
            locale_code=locale, key_id=path).first()
        if value:
            click.echo(
                f"Value in [{locale}] with path [{path}] already exists: [{value.gloss}]")
            click.echo("Nothing changed.")
        else:
            get_or_create(db.session, I18NKey, {'id': path})
            get_or_create(db.session, I18NLocale, {'code': locale})
            value = I18NValue(
                gloss=gloss,
                verified=False,
                key_id=path,
                locale_code=locale
            )
            db.session.add(value)
            db.session.commit()
            click.echo(
                f"Successfully added entry [{path}] in [{locale}] with [{gloss}]")

# --- flask i18n update

    @i18n_cli.command('update')
    @click.argument('locale', callback=validate_locale)
    @click.argument('path')
    @click.argument('gloss')
    def update_entry(locale, path, gloss):
        """ Update an entry in the database.

        No change will be made if the entry is not already in the database.

        To add entry, use the 'add' command.

        If change is made, the 'verified' flag will be set to False.

        Example usage:

        \b
            flask i18n update en-US actions.activate-account "Activate Account"
        """
        value = db.session.query(I18NValue).filter_by(
            locale_code=locale, key_id=path).first()
        if not value:
            click.echo(
                f"Value in [{locale}] with path [{path}] does not exist")
            click.echo("Nothing changed.")
        else:
            value.gloss = gloss
            value.verified = False
            db.session.add(value)
            db.session.commit()
            click.echo(
                f"Successfully updated entry [{path}] in [{locale}] with [{gloss}]")

# --- flask i18n delete

    @i18n_cli.command('delete', short_help="Delete entries from the database.")
    @click.option('-r', '--recursive', is_flag=True,
                  help="delete all entries starting with the given path")
    @click.option('--locale', callback=validate_locale_allow_none,
                  help="specify a given locale to delete, "
                  "leave empty to delete entry with all existing locales "
                  "along with its belong key and description")
    @click.option('-v/-s',
                  '--verbose/--silent',
                  is_flag=True,
                  default=True,
                  show_default=True,
                  help="Print output as modifying the database")
    @click.argument('path', callback=sanitize_path, default="")
    def delete_entries(recursive, locale, verbose, path):
        """ Delete I18NValue entries that match or start with PATH in the database.

        When PATH is not specified, all keys are deleted

        Example usage:

        \b
            flask i18n delete --locale en-US actions.activate-account

        \b
            flask i18n delete -r actions
        """
        value_query = db.session.query(I18NValue)
        key_query = db.session.query(I18NKey)

        if recursive:
            pattern = f"{path}.%" if path else "%"
            value_query = value_query.filter(
                I18NValue.key_id.like(pattern))
            key_query = key_query.filter(I18NKey.id.like(pattern))
        else:
            if not path:
                raise click.BadParameter(
                    f"Must specify a PATH when not using the --recursive flag")
            value_query = value_query.filter_by(key_id=path)
            key_query = key_query.filter_by(id=path)

        if locale:
            value_query = value_query.filter_by(locale_code=locale)
            # if only deleting a locale, don't delete the corresponding key
            key_query = key_query.filter(sqlalchemy.false())

        values = value_query.all()
        keys = key_query.all()
        if len(keys + values) == 0:
            click.echo("No entries found")
            if not recursive:
                click.echo(
                    "Hint: use the -r flag to delete recursively from an intermediate node")
            return

        if verbose:
            for value in values:
                click.echo(
                    f"Deleting value at [{value.key_id}] in [{value.locale_code}]: [{value.gloss}]")
            for key in keys:
                click.echo(
                    f"Deleting key [{key.id}] with description [{key.desc}]")

        count = 0
        # do not update the session for efficiency
        count += value_query.delete(synchronize_session=False)
        # do not update the session for efficiency
        count += key_query.delete(synchronize_session=False)
        db.session.commit()
        click.echo(f"Delete entry count: {count}")

# --- flask i18n edit

    @i18n_cli.command('edit', cls=ExceptionHandlingCommand,
                      short_help="Interactively edit entries.")
    @click.argument('path', callback=sanitize_path, default="")
    def edit_entries(path):
        """ Interactively edit entries that starts with PATH in an interactive editor,
        with a 'locale-tail' structured tree

        Example usage:

        \b
            flask i18n edit

            EDITOR=gedit flask i18n edit country.name
        """
        tree = read_locale_tail_tree(path)
        if tree:
            data = yaml.dump(tree, default_flow_style=False, sort_keys=True)
            comments = (
                "#####################################################################\n"
                "#             You are in the interactive editing mode \n"
                "# Start making some changes to the content and then save this file.\n"
                "#     Changes will be updated to the database. \n"
                "# Keys removed from the file will NOT be deleted from the database. \n"
                "#     To delete keys, see 'flask i18n delete --help'. \n"
                "# Close the editor without saving to abort the action.\n"
                "# \n"
                f"# Current path: {path or '(root)'}\n"
                "################## content above this line is ignored ###############\n\n")
            data = click.edit(comments + data, extension=".yaml")
            if data is None:
                click.echo("Content not saved, operation aborted.")
                raise click.Abort()
            try:
                tree = yaml.safe_load(data)
                result = write_locale_tail_tree(tree, path, verbose=True)
            except (yaml.YAMLError, BadTreeStructure) as e:
                click.echo(
                    "An error occurred writing the given yaml file to database")
                click.echo(f"Error message: {e}")
                click.echo("Saving content to a temporary file...")
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
                    filename = f.name
                    f.write(data)
                click.echo(f"Content saved to {filename}")
                click.echo("To save changes to the database, "
                           "remove any invalid blocks from the file and run:")
                click.echo(
                    f"\n    flask i18n import --target {filename} --override {path}\n")
            else:
                click.echo("Successfully edited entries")
                click.echo(f"Entry count: {result['entry_count']}")
        else:
            click.echo(f"No entries found")


# --- flask i18n translate


    @i18n_cli.command(
        'translate',
        cls=ExceptionHandlingCommand,
        short_help="Translate entries in the database.")
    @click.argument(
        'source-locale', callback=validate_locale, metavar="<src-locale>")
    @click.argument(
        'destination-locale',
        callback=validate_locale,
        metavar="<dest-locale>")
    @click.option(
        '-i',
        '--interactive',
        is_flag=True,
        default=False,
        help="interactively prompt for confirmation as the translation proceeds")
    @click.option(
        '--src-lang',
        callback=validate_language_allow_none,
        help="Manually provide a source language code to translate from")
    @click.option(
        '--dest-lang',
        help="Manually provide a destination language code to translate to")
    @click.option(
        '--delay-timer',
        type=click.FLOAT,
        default=0.3,
        help="A delay timer to prevent too frequent requests")
    def translate_entries(
            source_locale,
            destination_locale,
            src_lang,
            dest_lang,
            interactive,
            delay_timer
    ):
        """ Complete entries in the database with <dest-locale> by
        translating from <src-locale>.

        Example usage:

        \b
            flask i18n translate en-US es-EC
        """
        lang_map = googletrans.LANGUAGES

        # try to deduce source and destination language if not given
        src_lang = src_lang or next(
            (lang for lang in lang_map.keys()
             if lang[:2].lower() == source_locale[:2].lower()), None)
        if not src_lang:
            click.echo(get_formatted_language_map())
            click.echo(
                f"Cannot deduce source language from the given locale {source_locale}")
            click.echo(
                "Try to specify the source language with --src-lang explicitly")
            exit(1)

        # try to deduce source and destination language if not given
        dest_lang = dest_lang or next(
            (lang for lang in lang_map.keys()
             if lang[:2].lower() == destination_locale[:2].lower()), None)
        if not dest_lang:
            click.echo(get_formatted_language_map())
            click.echo(
                f"Cannot deduce destination language from the given locale {destination_locale}")
            click.echo(
                "Try to specify the destination language with --dest-lang explicitly")
            exit(1)

        t = googletrans.Translator()

        # start translation
        entry_count = 0
        all_keys = db.session.query(I18NKey).all()
        for key in all_keys:
            source_value, destination_value = None, None
            for value in key.values:
                if value.locale_code == source_locale:
                    source_value = value
                if value.locale_code == destination_locale:
                    destination_value = value
            if not source_value or destination_value:
                # skip if source doesn't exist or
                # there is already a destination value
                continue
            gloss = t.translate(
                source_value.gloss,
                src=src_lang,
                dest=dest_lang).text
            if interactive:
                click.echo(
                    f"[{key.id}] has no value in [{destination_locale}]")
                click.echo(
                    f"add translation [{source_value.gloss}] => [{gloss}]?")
                click.echo()
                options = {
                    'y': 'Yes, use the current translation',
                    'n': 'No, skip this entry',
                    'e': 'Edit the current entry',
                    'a': 'Use given translation for All following entries',
                    'q': 'Quit the program'
                }
                for k, v in options.items():
                    click.echo("{:3}: {}".format(k, v))
                choice = click.prompt(
                    "=> ",
                    type=click.Choice(
                        options.keys(),
                        case_sensitive=False),
                    default='y')
            else:
                choice = 'y'

            if choice == 'e':
                gloss = click.prompt(
                    "Enter a new translation to override the default one",
                    default=gloss)
                choice = 'y'
            elif choice == 'a':
                interactive = False
                choice = 'y'

            if choice == 'y':
                # make sure locale exists
                get_or_create(
                    db.session, I18NLocale, {
                        'code': destination_locale})
                destination_value = I18NValue(
                    key_id=key.id,
                    locale_code=destination_locale,
                    gloss=gloss,
                    verified=False
                )
                db.session.add(destination_value)
                entry_count += 1
                click.echo(f"Entry [{gloss}] added")
                if not interactive:
                    time.sleep(delay_timer)
            elif choice == 'n':
                click.echo(f"Entry [{gloss}] not added.")
                continue
            elif choice == 'q':
                click.echo("Nothing changed.")
                exit(0)
        db.session.commit()

        click.echo(f"Entry count: {entry_count}")

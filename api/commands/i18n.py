import json
import yaml
import click
import re
import os

from flask.cli import AppGroup
from src import BASE_DIR, db
from src.i18n.models import I18NLocale, I18NKey, I18NValue
from src.shared.helpers import tree_to_list, list_to_tree


# --- helpers

def is_valid_locale_code(locale_code):
    return re.fullmatch('[a-z]{2}-[A-Z]{2}', locale_code)


def validate_locale(ctx, param, value):
    """ a command option callback to make sure that the given string is a valid locale """
    if not is_valid_locale_code(value):
        raise click.BadParameter(
            f"{value} is not a valid locale code. It must be in the form of ab-XY")
    return value


def create_dir(ctx, param, value):
    """ a command option callback to create parent directories if does not exist """
    pardir = os.path.dirname(value.name)
    if pardir:
        os.makedirs(pardir, exist_ok=True)
    return value


def get_or_create(session, model, **kwargs):
    """get an item from the database, or create one if not exists
    credit: https://stackoverflow.com/a/6078058/6263602

    :session: the session object
    :model: the model for the table
    :**kwargs: filter criteria
    :returns: the object requested

    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def default_target():
    """ resolve the default target for dump/load commands based on the
    user-specified <locale> parameter
    """
    params = click.get_current_context().params
    if 'locale' not in params:
        click.echo(
            "Can't get default target from the specified <locale> parameter")
        raise click.Abort
    locale = params['locale']
    return os.path.join(BASE_DIR, 'i18n', f"{locale}.json")


def read_locale_tail_tree(parent_path=""):
    """read from the database entries starting with parent_path
    returns a valid "locale-tail" tree if possible.

    a "locale-tail" tree is a tree where each end entry contains
    its corresponding gloss in different locales, as opposed to
    a "locale-head" tree, where entry gloss themselves are
    categorized according to the locales.

    If it is impossible to create a valid tree, raise a RuntimeError

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
                raise RuntimeError(
                    f"Unexpected strip_key: [{list_item['path']}] does not start with [{strip_key}]")
        if key.desc:
            list_item['value']['_desc'] = key.desc
        return list_item

    parent_path = parent_path.strip('.')  # can't start or end with a dot
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

    :tree: the tree to be written into the database

    :parent_path: the path to which to append the tree

    :override: whether to override existing values in the database.
    if True, the 'verified' flag will be set to False after the update

    :returns: a result object:
    { entry_count: int, skip_count: int }
    """
    # make sure parent_path is not an entry
    parent_path = parent_path.strip('.')  # can't start or end with a dot
    if parent_path and db.session.query(
            I18NKey).filter_by(id=parent_path).count():
        raise RuntimeError(
            f"[{parent_path}] is already an entry, cannot write sub-entries onto that")

    entry_count, skip_count = 0, 0

    def is_leaf(node):
        return all([(key == '_desc' or is_valid_locale_code(key))
                    and isinstance(val, str) for key, val in node.items()])
    # if the given tree is a leaf
    if is_leaf(tree):
        # override the item specified by parent_path
        if not parent_path:
            raise RuntimeError(
                f"Must specify a path when overriding with a leaf node {tree}")
        lst = [{'path': [], 'value': tree}]
    # otherwise, flatten the given tree
    else:
        lst = tree_to_list(tree, is_leaf)
    for item in lst:
        key_id = '.'.join([parent_path] + item['path'])
        key = get_or_create(db.session, I18NKey, id=key_id)
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
                        db.session, I18NLocale, code=locale_code)
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


def create_i18n_cli(app):
    i18n_cli = AppGroup('i18n', help="Maintain translation entries.")

    @i18n_cli.command('load')
    @click.argument('locale', callback=validate_locale, metavar="<locale>")
    @click.option('--override/--no-override', default=True,
                  show_default=True,
                  help="Override if value already exists")
    @click.option('--target',
                  default=default_target,
                  show_default=os.path.join(BASE_DIR, 'i18n', "<locale>.json"),
                  type=click.File("r"),
                  help="The source file to load values from")
    def load_values(locale, target, override):
        """ Load values from a json file into the database.

        <locale>: the locale code of the processed values. E.g. en-US """
        entry_count = 0
        skip_count = 0
        locale_name = locale
        click.echo(f"loading values from [{target.name}]")
        tree = json.load(target)

        def is_leaf(node):
            return isinstance(node, dict) \
                and 'gloss' in node \
                and isinstance(node['gloss'], str)

        entries = tree_to_list(tree, is_leaf=is_leaf)
        locale = get_or_create(db.session, I18NLocale, code=locale_name)
        for entry in entries:
            key_id = '.'.join(entry['path'])
            key = get_or_create(db.session, I18NKey, id=key_id)
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
        db.session.commit()
        click.echo("Successfully loaded data into the database")
        click.echo(f"Source file: {target.name}")
        click.echo(f"Locale:      {locale_name}")
        click.echo(f"Entry count: {entry_count}")
        click.echo(f"Skip count:  {skip_count}")

    @i18n_cli.command('dump')
    @click.argument('locale', callback=validate_locale, metavar="<locale>")
    @click.option('--target',
                  default=default_target,
                  show_default=os.path.join(BASE_DIR, 'i18n', "<locale>.json"),
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to dump values to")
    def dump_values(locale, target):
        """ Dump values from the database into a json file.

        <locale>: the locale code of the processed values. E.g. en-US """
        click.echo(f"dumping values into {target.name}")
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
        click.echo(f"Target file: {target.name}")
        click.echo(f"Locale:      {locale}")
        click.echo(f"Entry count: {len(values)}")

    @i18n_cli.command('load-descriptions')
    @click.option('--override/--no-override',
                  default=False,
                  show_default=True,
                  help="Override if descriptions is non-empty")
    @click.option('--target',
                  default=os.path.join(BASE_DIR, 'i18n', "_desc.json"),
                  show_default=True,
                  type=click.File("r"),
                  help="The source file to load descriptions from")
    @click.option('--verbose/--no-verbose', default=False,
                  help="Print output as modifying the database")
    def load_descriptions(target, override, verbose):
        """ Load descriptions from a json file into the database. """
        entry_count = 0
        skip_count = 0
        tree = json.load(target)
        entries = tree_to_list(tree)
        click.echo(f"loading descriptions from [{target.name}]")
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
        click.echo(f"Source file: {target.name}")
        click.echo(f"Entry count: {entry_count}")
        click.echo(f"Skip count:  {skip_count}")
        if skip_count:
            click.echo(
                "Hint: use --override to load descriptions even if they exist")

    @i18n_cli.command('dump-descriptions')
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
        help="The description to use when the description in database is not given or empty,"
        " must be used with --dump-empty to take effect")
    @click.option('--target',
                  default=os.path.join(BASE_DIR, 'i18n', "_desc.json"),
                  show_default=True,
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to dump descriptions to")
    def dump_descriptions(target, dump_empty, empty_placeholder):
        """ Dump descriptions into a json file from the database. """
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
        click.echo(f"Target file: {target.name}")
        click.echo(f"Entry count: {len(keys)}")

    @i18n_cli.command('export')
    @click.argument('path', default="")
    @click.option('--target',
                  default='-',
                  show_default=True,
                  callback=create_dir,
                  type=click.File("w"),
                  help="The destination file to export the tree to")
    def export_entries(path, target):
        """ list all entries that starts with PATH in a 'locale-tail' structured tree """
        tree = read_locale_tail_tree(path)
        yaml.dump(tree, target, default_flow_style=False, sort_keys=True)

    @i18n_cli.command('import')
    @click.argument('path', default="")
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
    @click.option('--verbose/--no-verbose', default=False,
                  help="Print output as modifying the database")
    def import_entries(path, target, override, verbose):
        """ load all entries expressed in a 'locale-tail' structured tree into the database,
        prepend each entry's path with PATH """
        tree = yaml.safe_load(target)
        result = write_locale_tail_tree(tree, path, override, verbose)
        click.echo("Successfully loaded data into the database")
        click.echo(f"Source file: {target.name}")
        click.echo(f"Entry count: {result['entry_count']}")
        click.echo(f"Skip count:  {result['skip_count']}")

    app.cli.add_command(i18n_cli)

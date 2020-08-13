import hashlib

from flask.json import jsonify

from flask import current_app

from src import db

from sqlalchemy.exc import DBAPIError

from .models import QueryArgumentError


def modify_entity(entity_type, schema, id, new_value_dict):
    item = db.session.query(entity_type).filter_by(id=id).first()

    if not item:
        return jsonify(f"Item with id #{id} does not exist."), 404

    for key, val in new_value_dict.items():
        if key != 'id':
            setattr(item, key, val)

    db.session.commit()

    return jsonify(schema.dump(item)), 200


def get_exclusion_list(query_object, default_exclusion_list):
    ret_list = default_exclusion_list.copy()
    for exclusion in default_exclusion_list:
        include_filter = query_object.get(f"include_{exclusion}")
        if include_filter:
            ret_list.remove(exclusion)
    return ret_list


def get_all_queried_entities(query_object, request_query_arguments):
    """ append a list of filters, and return the result

    query_object: a session.query object
    request_query_arguments: a dictionary of query arguments from the incoming request

    valid query arguments: offset, limit, where, order
    invalid ones will be ignored
    for 'where' and 'order', the value of the query should be in the form of 'key:value'

    example queries:
    /groups?offset=20
    /groups?where=active:true&where=name:Adult

    Return value:

    Returns the queried list of entities

    Exceptions:

    When the given query value is not in the correct form (e.g. the 'where' or 'order' query does not contain a ':' in the value), a QueryArgumentError with proper error message will be raised. More types of exceptions can be added in the future, but that will require the endpoints to include logic to handle those errors as well.

    This is intended to be used in most of the read_all_* endpoints

    """
    def parse_kv_str(kv_str):
        """ return a list [k,v] from string 'k:v' """
        kv_lst = kv_str.split(':', 1)
        if len(kv_lst) != 2:
            raise QueryArgumentError(
                f"The given value '{kv_str}' is not in the 'key:value' form", 422)
        return kv_lst

    # offset
    offset = request_query_arguments.get('offset')
    if offset:
        query_object = query_object.offset(offset)

    # limit
    limit = request_query_arguments.get('limit')
    if limit:
        query_object = query_object.limit(limit)

    # Get the columns of current table
    columns = query_object.column_descriptions[0]['type'].__table__.columns
    columns_map = {c.key: c for c in columns}

    # where, can be a list of multiple values
    where_key_value_strings = request_query_arguments.getlist('where')
    # sqlalchemy will automatically translate strings into boolean and/or
    # integer
    if where_key_value_strings:
        where_dict = {}
        for kv_str in where_key_value_strings:
            kv_lst = parse_kv_str(kv_str)
            if kv_lst[0] not in columns_map:
                raise QueryArgumentError(
                    f"Error in 'where' query: There is no column named '{kv_lst[0]}'", 404)
            where_dict[kv_lst[0]] = kv_lst[1]
        query_object = query_object.filter_by(**where_dict)

    # order, can be a list of multiple values
    order_key_value_strings = request_query_arguments.getlist('order')
    if order_key_value_strings:
        order_lst = []
        for kv_str in order_key_value_strings:
            kv_lst = parse_kv_str(kv_str)
            if kv_lst[0] not in columns_map:
                raise QueryArgumentError(
                    f"Error in 'order' query: There is no column named '{kv_lst[0]}'", 404)
            if kv_lst[1] == 'asc':
                order_lst.append(columns_map[kv_lst[0]].asc())
            elif kv_lst[1] == 'desc':
                order_lst.append(columns_map[kv_lst[0]].desc())
            else:
                raise QueryArgumentError(
                    f"Error in 'order' query: Invalid order type '{kv_lst[1]}', must be either 'asc' or 'desc'",
                    422)

        query_object = query_object.order_by(*order_lst)

    try:
        all_entities = query_object.all()
    # catch errors raised from the database
    except DBAPIError as e:
        raise QueryArgumentError(repr(e), 422)
    return all_entities


def logged_response(body, code=200):
    """ intends to be used as a wrapper before an endpoint returns
    to log information to the console and file using app.logger

    body: the body to be converted to a Response,
        if it is not a string, it will be 'jsonified'
    code: the response status code, default to 200 be used

    """

    if current_app:
        if code >= 400:
            logger = current_app.logger.warning
        else:
            logger = current_app.logger.info

        logger(f"{body} --- {code}")
    return jsonify(body), code


def is_allowed_file(filename):
    return '.' in filename and \
           get_file_extension(filename) in set(['png', 'jpg', 'jpeg', 'gif'])


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def get_hash(filename):
    return hashlib.sha1(str(filename).encode('utf-8')).hexdigest()


class BadTreeStructure(Exception):
    pass


class BadListKeyPath(Exception):
    pass


def tree_to_list(tree, is_leaf=lambda node: isinstance(node, str)):
    """ convert a tree into a list of { 'path': 'abc.xyz', 'value': leaf_node }
    where is_leaf(leaf_node) == True

    raises a BadTreeStructure error if cannot convert the given tree
    """
    result = []

    def tree_to_list_helper(word_map, path=[]):
        if not isinstance(word_map, dict):
            raise BadTreeStructure(
                f"node [{word_map}] at path [{'.'.join(path)}]"
                " is neither a valid dictionary nor a valid leaf node")
        for key, val in word_map.items():
            if (is_leaf(val)):
                result.append({'path': path + [key], 'value': val})
            else:
                tree_to_list_helper(val, path + [key])
    tree_to_list_helper(tree)
    return result


def list_to_tree(entries):
    """ convert a list of { 'path': 'abc.xyz', 'value': node } into a tree
    {
      'abc': {
        'xyz': node
      }
    }

    raises a BadListKeyPath error if cannot convert the given list to a valid tree
    """
    tree = {}
    for entry in entries:
        keys = entry['path'].split('.')
        t = tree
        but_last, last = keys[:-1], keys[-1]
        for i, key in enumerate(but_last):
            t = t.setdefault(key, {})
            if not isinstance(t, dict):
                raise BadListKeyPath(
                    f"failed to add child [{key}] in path [{entry['path']}], "
                    f"non-dict value [{t}] at [{'.'.join(but_last[:i+1])}]")
        if last not in t:
            t[last] = entry['value']
        else:
            raise BadListKeyPath(
                f"{entry['path']} already exists: '{t[last]}', won't set to '{entry['value']}'")
    return tree


def get_or_create(session, model, filters, attributes={}):
    """get an item from the database, or create one if not exists
    credit: https://stackoverflow.com/a/6078058/6263602

    :session: the session object
    :model: the model for the table
    :filters: the filters to be applied
    :attributes: the attributes to be added to the created instance
    :returns: the object requested

    """
    instance = session.query(model).filter_by(**filters).first()
    if instance:
        return instance
    else:
        instance = model(**{**filters, **attributes})
        session.add(instance)
        session.commit()
        return instance



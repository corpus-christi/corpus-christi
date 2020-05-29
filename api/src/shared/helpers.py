import hashlib

from flask.json import jsonify

from src import db

from sqlalchemy.exc import DBAPIError


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

    When the given query value is not in the correct form (e.g. the 'where' or 'order' query does not contain a ':' in the value), an ValueError with proper response will be raised

    When any other error occurs when executing the statement (e.g. a string given to 'offset'), a DBAPIError will be raised

    This is intended to be used in most of the read_all_* endpoints
    
    """
    # TODO: When the given query value is invalid, a database error will occur, and this needs to be detected <2020-05-29, David Deng> #
    def parse_kv_str(kv_str):
        """ return a list [k,v] from string 'k:v' """
        kv_lst = kv_str.split(':', 1)
        if len(kv_lst) != 2:
            raise ValueError(f"The given value '{kv_str}' is not in the 'key:value' form")
        return kv_lst

    # offset
    offset = request_query_arguments.get('offset')
    if offset:
        query_object = query_object.offset(offset)

    # limit
    limit = request_query_arguments.get('limit')
    if limit:
        query_object = query_object.limit(limit)

    columns = query_object.column_descriptions[0]['type'].__table__.columns
    columns_map = { c.key: c for c in columns }
    print("columns_map: {}".format(columns_map))

    # where
    where_key_value_strings = request_query_arguments.getlist('where')
    # sqlalchemy will automatically translate strings into boolean  and integer
    if where_key_value_strings:
        where_dict = { kv_lst[0]: kv_lst[1] for kv_lst in [ parse_kv_str(kv_str) for kv_str in where_key_value_strings ] }
        query_object = query_object.filter_by(**where_dict)

    # # order
    # order_key_value_string = request_query_arguments.get('order')
    # if order_key_value_string:
    #     order_kv_lst = parse_kv_str(order_key_value_string)

    try:
        all_entities = query_object.all()
    except Exception as e:
        print(e)
        raise e
    return all_entities



def is_allowed_file(filename):
    return '.' in filename and \
           get_file_extension(filename) in set(['png', 'jpg', 'jpeg', 'gif'])


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def get_hash(filename):
    return hashlib.sha1(str(filename).encode('utf-8')).hexdigest()

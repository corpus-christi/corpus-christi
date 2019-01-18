from flask.json import jsonify
from .. import db

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
    for exclusion in default_exclusion_list:
        include_filter = query_object.get(f"include_{exclusion}")
        if include_filter:
            default_exclusion_list.remove(exclusion)
    return default_exclusion_list

def is_allowed_file(filename):
    return '.' in filename and \
         get_file_extension(filename) in set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

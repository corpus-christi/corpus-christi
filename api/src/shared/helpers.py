import hashlib
from typing import Any, Dict, Optional, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session


def modify_entity(db: Session, entity_type, id: Any, new_value_dict: Dict):
    """Update an entity by id with the given values dict."""
    item = db.get(entity_type, id)

    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id #{id} does not exist.")

    for key, val in new_value_dict.items():
        if key != 'id':
            setattr(item, key, val)

    db.commit()
    db.refresh(item)
    return item


def get_exclusion_list(query_params: Dict, default_exclusion_list):
    """Return list of fields to exclude based on query parameters."""
    ret_list = default_exclusion_list.copy()
    for exclusion in default_exclusion_list:
        include_filter = query_params.get(f"include_{exclusion}")
        if include_filter:
            ret_list.remove(exclusion)
    return ret_list


def is_allowed_file(filename: str) -> bool:
    return '.' in filename and \
           get_file_extension(filename) in {'png', 'jpg', 'jpeg', 'gif'}


def get_file_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[1].lower()


def get_hash(file_obj) -> str:
    return hashlib.sha1(str(file_obj).encode('utf-8')).hexdigest()

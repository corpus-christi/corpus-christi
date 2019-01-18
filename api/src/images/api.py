import json
import os
import hashlib
from datetime import datetime, timedelta

from flask import request, send_file
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt, jwt_optional
from flask_mail import Message
from marshmallow import ValidationError
from sqlalchemy import func

from . import images
from .. import db, mail, BASE_DIR
from ..etc.helper import modify_entity, get_exclusion_list, is_allowed_file, get_file_extension
from .models import Image, ImageSchema, ImageEvent, ImageEventSchema

# ---- Image

image_schema = ImageSchema()

@images.route('/<image_id>')
@jwt_required
def download_image(image_id):
    image = db.session.query(Image).filter_by(id=image_id).first()

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    image_path = BASE_DIR + '/' + image.path

    return send_file(image_path, mimetype='image/jpg')

@images.route('/', methods=['POST'])
@jwt_required
def upload_image():
    # -- POST request should be sent with image as binary data...
    # Example:
    # json = {'Description' : 'This is a picture'}
    # requests.post('/images/', data=open('your_image.png','rb').read(), json=json)
    
    if request.files['image']:
        image = request.files['image']
    else:
        return 'No image selected', 422

    if request.form['data']:
        data = json.loads(request.form['data'])
        try:
            valid_desc = image_schema.load(data, partial=('path', 'id'))
        except ValidationError as err:
            return jsonify(err.messages), 422

    if is_allowed_file(image.filename):
        file_hash = hashlib.sha1(str(image.filename).encode('utf-8')).hexdigest()
        new_filename = file_hash + '.' + get_file_extension(image.filename)
        folder_path = BASE_DIR + '/data/images/'
        full_path = folder_path + new_filename
        image_already_in_db = db.session.query(Image).filter_by(path=full_path).first()
        if image_already_in_db:
            return 'Image already exists', 422
        image.save(os.path.join(folder_path, new_filename))
    else:
        return 'Invalid image', 422

    valid_image = dict()
    valid_image['path'] = full_path
    if valid_desc:
        valid_image['description'] = data['description']

    valid_image = image_schema.load(valid_image, partial=True)

    new_image = Image(**valid_image)
    db.session.add(new_image)
    db.session.commit()

    return 'Image successfully uploaded', 201

@images.route('/<image_id>', methods=['PUT'])
@jwt_required
def replace_image(image_id):
    try:
        valid_image = image_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_entity(Image, image_schema, image_id, valid_image)


@images.route('/<image_id>', methods=['PATCH'])
@jwt_required
def update_image(image_id):
    try: 
        valid_attributes = image_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
                
    return modify_entity(Image, image_schema, image_id, valid_attributes)


@images.route('/<image_id>', methods=['DELETE'])
@jwt_required
def delete_image(image_id):
    image = db.session.query(Image).filter_by(id=image_id).first()

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404
        
    db.session.delete(image)
    db.session.commit()
    
    # 204 codes don't respond with any content
    return "Deleted successfully", 204

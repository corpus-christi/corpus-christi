import os

from flask import request, send_file
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from . import images
from .models import Image, ImageSchema
from .. import db, BASE_DIR
from src.shared.helpers import modify_entity, is_allowed_file, get_file_extension, \
        get_hash, get_all_queried_entities

# ---- Image

image_schema = ImageSchema()
image_schema_partial = ImageSchema(partial=('id', 'path', 'events'))


@images.route('/<image_id>')
def download_image(image_id):
    base_dir = BASE_DIR + '/'
    image = db.session.query(Image).filter_by(id=image_id).first()

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    image_path = os.path.join(base_dir, image.path)

    return send_file(image_path, mimetype='image/jpg')


@images.route('/', methods=['POST'])
@jwt_required
def upload_image():
    # -- POST request should be sent with image in request.files['file'] &
    # description in request.form['data'] as a json object (e.g. {'description': 'this is a picture.'})
    base_dir = BASE_DIR + '/'
    if request.files:
        if request.files['file']:
            image = request.files['file']
        else:
            return 'No image file found in "files" section', 422
    else:
        return 'No image selected', 422

    # Grab a description from the request if there is one
    valid_desc = None
    if request.form:
        if request.form['description']:
            valid_desc = True

    # Safely convert the filename into an ASCII only string
    filename = secure_filename(image.filename)

    # Check to make sure the file is of an acceptable type
    if is_allowed_file(filename):
        file_hash = get_hash(image)
        folder = file_hash[0:2]
        new_filename = file_hash + '.' + get_file_extension(filename)

        folder_path = os.path.join('data/', folder)

        # Create a folder that is the first two characters of the file hash
        if not os.path.exists(os.path.join(base_dir, folder_path)):
            os.makedirs(os.path.join(base_dir, folder_path))

        path_to_image = os.path.join(folder_path, new_filename)
        image_already_in_db = db.session.query(Image).filter_by(path=path_to_image).first()

        # return a directive to look up the existing image
        if image_already_in_db:
            return jsonify({
                'message': 'Identical image already exists',
                'id': image_already_in_db.id
            }), 303

        # Save the image into the file system
        full_path = os.path.join(base_dir, path_to_image)
        image.save(full_path)
    else:
        return 'Invalid file type', 422

    # Create and store the image object into the db
    valid_image = dict()
    valid_image['path'] = path_to_image
    if valid_desc:
        valid_image['description'] = request.form['description']

    valid_image = image_schema.load(valid_image, partial=True)

    new_image = Image(**valid_image)
    db.session.add(new_image)
    db.session.commit()

    return jsonify(image_schema.dump(new_image)), 201

@images.route('/', methods=['GET'])
@jwt_required
def read_all_images():
    query = db.session.query(Image)
    try:
        images = get_all_queried_entities(query, request.args)
    except QueryArgumentError as e:
        return jsonify(e.message), e.code
    return jsonify(image_schema.dump(images, many=True))


@images.route('/<image_id>', methods=['PATCH'])
@jwt_required
def update_image(image_id):
    # -- PATCH can only be used to update an image's description
    try:
        valid_attributes = image_schema_partial.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    return modify_entity(Image, image_schema_partial, image_id, valid_attributes)


@images.route('/<image_id>', methods=['DELETE'])
@jwt_required
def delete_image(image_id):
    image = db.session.query(Image).filter_by(id=image_id).first()

    if not image:
        return jsonify(f"Image with id #{image_id} does not exist."), 404

    os.remove(os.path.join(BASE_DIR, image.path))

    db.session.delete(image)
    db.session.commit()

    # 204 codes don't respond with any content
    return "Deleted successfully", 204

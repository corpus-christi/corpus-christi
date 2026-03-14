import hashlib
import os
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import BASE_DIR
from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import Image, ImageRead
from ..shared.helpers import is_allowed_file, get_file_extension

router = APIRouter()


def get_hash(file_content: bytes) -> str:
    return hashlib.sha1(file_content).hexdigest()


@router.get("/{image_id}")
def download_image(image_id: int, db: Session = Depends(get_db)):
    base_dir = BASE_DIR + '/'
    image = db.get(Image, image_id)

    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")

    image_path = os.path.join(base_dir, image.path)
    return FileResponse(image_path, media_type='image/jpeg')


@router.post("/", response_model=ImageRead, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    base_dir = BASE_DIR + '/'

    filename = file.filename or ""
    if not is_allowed_file(filename):
        raise HTTPException(status_code=422, detail="Invalid file type")

    file_content = await file.read()
    file_hash = get_hash(file_content)
    folder = file_hash[0:2]
    new_filename = file_hash + '.' + get_file_extension(filename)

    folder_path = os.path.join('data/', folder)
    if not os.path.exists(os.path.join(base_dir, folder_path)):
        os.makedirs(os.path.join(base_dir, folder_path))

    path_to_image = os.path.join(folder_path, new_filename)

    image_already_in_db = db.execute(
        select(Image).where(Image.path == path_to_image)
    ).scalar_one_or_none()
    if image_already_in_db:
        raise HTTPException(
            status_code=303,
            detail={'message': 'Identical image already exists', 'id': image_already_in_db.id}
        )

    full_path = os.path.join(base_dir, path_to_image)
    with open(full_path, 'wb') as f:
        f.write(file_content)

    new_image = Image(path=path_to_image, description=description)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@router.patch("/{image_id}", response_model=ImageRead)
def update_image(
    image_id: int,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")
    if description is not None:
        image.description = description
    db.commit()
    db.refresh(image)
    return image


@router.delete("/{image_id}", status_code=204)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with id #{image_id} does not exist.")

    full_path = os.path.join(BASE_DIR, image.path)
    if os.path.exists(full_path):
        os.remove(full_path)

    db.delete(image)
    db.commit()

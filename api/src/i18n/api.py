from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from .models import (
    I18NLocale, I18NLocaleCreate, I18NLocaleRead,
    I18NKey, I18NKeyCreate, I18NKeyRead,
    I18NValue, I18NValueCreate, I18NValueRead,
    Language
)

router = APIRouter()


# ---- I18N Locale

@router.get("/locales", response_model=list[I18NLocaleRead])
def read_all_locales(db: Session = Depends(get_db)):
    return db.execute(select(I18NLocale)).scalars().all()


@router.get("/locales/{locale_code}", response_model=I18NLocaleRead)
def read_one_locale(locale_code: str, db: Session = Depends(get_db)):
    locale = db.execute(
        select(I18NLocale).where(I18NLocale.code == locale_code)
    ).scalar_one_or_none()
    if locale is None:
        raise HTTPException(status_code=404, detail="No such locale")
    return locale


@router.post("/locales", response_model=I18NLocaleRead, status_code=201)
def create_locale(
    payload: I18NLocaleCreate,
    db: Session = Depends(get_db),
    _: I18NLocale = Depends(get_current_user)
):
    new_locale = I18NLocale(**payload.model_dump())
    db.add(new_locale)
    db.commit()
    db.refresh(new_locale)
    return new_locale


@router.delete("/locales/{locale_code}", status_code=204)
def delete_one_locale(
    locale_code: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    locale = db.get(I18NLocale, locale_code)
    if locale is None:
        raise HTTPException(status_code=404, detail="Locale not found")
    db.delete(locale)
    db.commit()


# ---- I18N Key

@router.get("/keys", response_model=list[I18NKeyRead])
def read_all_keys(db: Session = Depends(get_db)):
    return db.execute(select(I18NKey)).scalars().all()


@router.get("/keys/{key_id}", response_model=I18NKeyRead)
def read_one_key(key_id: str, db: Session = Depends(get_db)):
    key = db.execute(
        select(I18NKey).where(I18NKey.id == key_id)
    ).scalar_one_or_none()
    if key is None:
        raise HTTPException(status_code=404, detail="No such key")
    return key


@router.post("/keys", response_model=I18NKeyRead, status_code=201)
def create_key(
    payload: I18NKeyCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    new_key = I18NKey(**payload.model_dump())
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key


# ---- I18N Value

@router.get("/values", response_model=list[I18NValueRead])
def read_all_values(db: Session = Depends(get_db)):
    return db.execute(select(I18NValue)).scalars().all()


@router.get("/values/{locale_code}")
def read_xlation(
    locale_code: str,
    format: Optional[str] = Query("list"),
    db: Session = Depends(get_db)
):
    locale = db.execute(
        select(I18NLocale).where(I18NLocale.code == locale_code)
    ).scalar_one_or_none()
    if locale is None:
        raise HTTPException(status_code=404, detail="Locale not found")

    values = db.execute(
        select(I18NValue).where(I18NValue.locale_code == locale_code)
    ).scalars().all()

    if format == 'list':
        return [{"key_id": v.key_id, "locale_code": v.locale_code, "gloss": v.gloss} for v in values]
    elif format == 'tree':
        tree = {}
        for value in values:
            t = tree
            keys = value.key_id.split('.')
            for idx, key in enumerate(keys):
                if idx < len(keys) - 1:
                    t = t.setdefault(key, {})
                else:
                    if isinstance(t, dict):
                        t[key] = value.gloss
                    else:
                        raise HTTPException(status_code=400, detail=f'Invalid key ({value.key_id})')
        return tree
    else:
        raise HTTPException(status_code=400, detail="Invalid format")


# ---- Language

@router.get("/languages")
@router.get("/languages/{language_code}")
def read_languages(
    language_code: Optional[str] = None,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if locale is None:
        raise HTTPException(status_code=400, detail="Missing locale")

    if language_code is None:
        result = db.execute(
            select(Language.code, I18NValue.gloss)
            .join(I18NKey, Language.name_i18n == I18NKey.id)
            .join(I18NValue, I18NKey.id == I18NValue.key_id)
            .where(I18NValue.locale_code == locale)
        ).all()
        return [{"code": r[0], "name": r[1]} for r in result]
    else:
        result = db.execute(
            select(Language.code, I18NValue.gloss)
            .where(Language.code == language_code)
            .join(I18NKey, Language.name_i18n == I18NKey.id)
            .join(I18NValue, I18NKey.id == I18NValue.key_id)
            .where(I18NValue.locale_code == locale)
        ).first()
        if result is None:
            return {}
        return {"code": result[0], "name": result[1]}

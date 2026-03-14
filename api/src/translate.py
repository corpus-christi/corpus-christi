from sqlalchemy import select

from .db import SessionLocal
from .i18n.models import I18NValue


def getTranslation(locale_code, i18n_key):
    with SessionLocal() as db:
        res = db.execute(
            select(I18NValue).where(I18NValue.key_id == i18n_key, I18NValue.locale_code == locale_code)
        ).scalar_one_or_none()
    return res

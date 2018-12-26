from sqlalchemy import String


class StringTypes:
    SHORT_STRING = String(16)
    MEDIUM_STRING = String(64)
    LONG_STRING = String(255)

    I18N_KEY = String(32)
    LOCALE_CODE = String(5)
    PASSWORD_HASH = String(128)

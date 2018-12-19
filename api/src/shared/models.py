from .. import orm


class StringTypes:
    SHORT_STRING = orm.String(16)
    MEDIUM_STRING = orm.String(64)
    LONG_STRING = orm.String(255)
    I18N_KEY = orm.String(32)
    LOCALE_CODE = orm.String(5)

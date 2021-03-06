from sqlalchemy import String


class StringTypes:
    SHORT_STRING = String(16)
    MEDIUM_STRING = String(64)
    LONG_STRING = String(255)
    LONG_LONG_STRING = String(4096)

    I18N_KEY = String(255)
    LOCALE_CODE = String(5)
    PASSWORD_HASH = String(128)


class QueryArgumentError(Exception):
    def __init__(self, message, code, *args):
        """ represents an error in the query arguments of a request """
        super().__init__(message, code, *args)
        self.message = message
        self.code = code

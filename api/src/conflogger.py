from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {
        'brief': {
            'format': '[%(asctime)s] %(levelname)-8s from <%(funcName)s>: %(message)s',
            },
        'precise': {
            'format': '[%(asctime)s] %(levelname)-8s from %(pathname)s:%(lineno)d, <%(funcName)s>: %(message)s',
            },
        },
    'handlers': {
        # log to stdout
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'brief',
            'level': 'INFO'
            },
        # log to file
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/conflogger.log',
            'maxBytes': 1024,
            'backupCount': 5,
            'mode': 'a+',
            'formatter': 'precise',
            'level': 'WARNING'
            }
        },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
        }
    })

from logging import Formatter
from logging.config import dictConfig
from flask import has_request_context, request

class RequestFormatter(Formatter):
    """ a custom formatter including injected request information """
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.path = request.path
            record.method = request.method
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.path = None
            record.method = None
            record.remote_addr = None

        return super().format(record)

dictConfig({
    'version': 1,
    'formatters': {
        'brief': {
            '()': RequestFormatter, # constructor
            'format': '[%(asctime)s] %(levelname)-7s %(method)-6s from <%(path)s>: %(message)s',
            },
        'precise': {
            '()': RequestFormatter,
            'format': '[%(asctime)s] %(levelname)-7s %(method)-6s from <%(url)s> (%(remote_addr)s): %(message)s',
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

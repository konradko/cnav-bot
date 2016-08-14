from __future__ import absolute_import

import logging
from logging.config import dictConfig

from cnavbot import settings


dictConfig({
    'version': 1,
    'formatters': {
        'formatter': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': settings.BOT_LOG_PATH,
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'formatter',
            'level': logging.DEBUG,
        }
    },
    'root': {
        'handlers': [
            'rotating_file'
        ],
        'level': logging.DEBUG,
    },
})

logger = logging.getLogger()

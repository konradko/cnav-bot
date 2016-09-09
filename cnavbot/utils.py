from contextlib import contextmanager
import logging.config

from cnavbot import settings


logger = logging.getLogger()


@contextmanager
def cleanup(bot):
    try:
        yield bot
    finally:
        bot.cleanup()


@contextmanager
def sentry():
    try:
        yield
    except:
        if settings.SENTRY_CLIENT:
            # prints traceback
            logging.exception("Exception occurred, sending to Sentry:")
            settings.SENTRY_CLIENT.captureException()
        else:
            raise

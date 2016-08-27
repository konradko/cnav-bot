from contextlib import contextmanager
import logging

from cnavbot import settings


@contextmanager
def cleanup(bot):
    try:
        yield bot
    finally:
        bot.cleanup()


def sentry(func):
    """
    Decorator that sends exceptions to app.getsentry.com if SENTRY_DSN env var
    is set.
    """
    def wrapped(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            if settings.SENTRY_CLIENT:
                # prints traceback
                logging.exception("Exception occurred, sending to Sentry:")
                settings.SENTRY_CLIENT.captureException()
            else:
                raise
    return wrapped

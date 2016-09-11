from contextlib import contextmanager
import logging


@contextmanager
def cleanup(bot):
    try:
        yield bot
    finally:
        bot.cleanup()


@contextmanager
def log_exceptions():
    try:
        yield
    except:
        logging.exception('Exception: ')
        raise

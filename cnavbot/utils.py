from contextlib import contextmanager
import logging.config

logger = logging.getLogger()


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
        logging.exception()
        raise

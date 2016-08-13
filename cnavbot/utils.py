from contextlib import contextmanager
import logging
import time

import picamera

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


def wait_till_switch_pressed():
    while True:
        if settings.BOT_DRIVER.getSwitch():
            return
        else:
            time.sleep(0.5)


def take_picture_continously(interval=15, save_to='/data/bot.jpg'):
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        while True:
            time.sleep(interval)
            camera.capture(save_to)

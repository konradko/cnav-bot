import os
import sys
import logging

sys.path.append(os.getcwd())

from cnavbot import settings
from cnavbot.utils import log_exceptions
from cnavbot.services import bot, bluetooth, camera


logger = logging.getLogger()


def run():
    logger.info("Starting...")

    if settings.BOT_ENABLED:
        bot.Service().start()

    if settings.BLUETOOTH_ENABLED:
        bluetooth.Service().start()

    if settings.CAMERA_ENABLED:
        camera.Service().start()

    logger.info("Done")


if __name__ == '__main__':
    with log_exceptions():
        if settings.RUNNING_ON_PI:
            run()
        else:
            logger.warning("Not running on a Raspberry Pi")

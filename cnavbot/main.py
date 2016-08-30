from cnavbot import settings
from cnavbot.utils import sentry, logger
from cnavbot.services import bot, bluetooth, camera


@sentry
def run():
    logger.info("Starting...")

    bot.Service().start()
    bluetooth.Service().start()
    camera.Service().start()

    logger.info("Done")


if __name__ == '__main__':
    if settings.RUNNING_ON_PI:
        run()
    else:
        logger.warning("Not running on a Raspberry Pi")

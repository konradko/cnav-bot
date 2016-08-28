from cnavbot import settings
from cnavbot.utils import sentry, logger
from cnavbot.bot import api, bluetooth, camera


@sentry
def run():
    logger.info("Starting...")

    bluetooth.Service().run()
    camera.Service().run()
    api.Service().run()

    logger.info("Done")


if __name__ == '__main__':
    if settings.RUNNING_ON_PI:
        run()
    else:
        logger.warning("Not running on a Raspberry Pi")

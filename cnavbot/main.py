from cnavbot import api, utils, settings, logger


@utils.sentry
def run():
    logger.info("Starting...")
    with utils.cleanup(api.Bot()) as bot:
        bot.wait_till_switch_pressed()
        if settings.BOT_IN_WANDER_MODE:
            bot.wander_continuously()
        if settings.BOT_IN_FOLLOW_MODE:
            bot.follow_line_continuously()
    logger.info("Done")


if __name__ == '__main__':
    if settings.RUNNING_ON_PI:
        run()
    else:
        logger.warning("Not running on a Raspberry Pi")

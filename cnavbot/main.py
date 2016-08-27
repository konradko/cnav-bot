from cnavbot import api, camera, bluetooth, utils, settings, logger


@utils.sentry
def run():
    logger.info("Starting...")
    bluetooth.Service().run()
    camera.Service().run()
    with utils.cleanup(api.Bot()) as bot:
        if settings.BOT_WAIT_FOR_BUTTON_PRESS:
            bot.wait_till_switch_pressed()
        if settings.BOT_IN_WANDER_MODE:
            bot.wander_continuously()
        elif settings.BOT_IN_FOLLOW_MODE:
            bot.follow_line_continuously()
        elif settings.BOT_IN_FOLLOW_AVOID_MODE:
            bot.follow_line_and_avoid_obstacles_continuously()
    logger.info("Done")


if __name__ == '__main__':
    if settings.RUNNING_ON_PI:
        run()
    else:
        logger.warning("Not running on a Raspberry Pi")

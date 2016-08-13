from cnavbot import api, utils, settings


if settings.RUNNING_ON_PI:
    with utils.cleanup(api.Bot()) as bot:
        bot.wait_till_switch_pressed()
        bot.wander()

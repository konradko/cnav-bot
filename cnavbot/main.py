from cnavbot import api, utils, settings


if settings.RUNNING_ON_PI:
    bot = api.Bot()
    utils.wait_till_switch_pressed()
    bot.wander()

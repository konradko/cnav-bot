import os
import platform


# Must be between 0 and 100
BOT_DEFAULT_SPEED = os.getenv('BOT_DEFAULT_SPEED', 50)

BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', platform.node())

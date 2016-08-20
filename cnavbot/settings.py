import os

from raven import Client


_, HOSTNAME, _, _, MACHINE = os.uname()
RUNNING_ON_PI = (
    HOSTNAME.startswith('raspberrypi') and MACHINE.startswith('arm')
)

# Driver libs can only be installed on RPi
if RUNNING_ON_PI:
    from pi2go import pi2go  # noqa
    BOT_DRIVER = pi2go

    import bluetooth  # noqa
    BLUETOOTH_DRIVER = bluetooth._bluetooth

    from ibeaconscanner import blescan  # noqa
    IBEACON_SCANNER = blescan
else:
    BOT_DRIVER = None
    BLUETOOTH_DRIVER = None
    IBEACON_SCANNER = None

# 'wander' (roam freely) or 'follow' (follow line)
BOT_MODE_WANDER = 'wander'
BOT_MODE_FOLLOW = 'follow'
BOT_MODE = os.getenv('BOT_MODE', BOT_MODE_WANDER)
BOT_IN_WANDER_MODE = False
BOT_IN_FOLLOW_MODE = False

if BOT_MODE == BOT_MODE_WANDER:
    BOT_IN_WANDER_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW:
    BOT_IN_FOLLOW_MODE = True

# Must be between 0 and 100
BOT_DEFAULT_SPEED = int(os.getenv('BOT_DEFAULT_SPEED', 30))
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)
BOT_DEFAULT_MAX_DISTANCE = int(os.getenv('BOT_DEFAULT_MAX_DISTANCE', 10))
BOT_LOG_PATH = os.environ.get('BOT_LOG_PATH', '/tmp/cnavbot.log')

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
SENTRY_CLIENT = Client(SENTRY_DSN) if SENTRY_DSN else None

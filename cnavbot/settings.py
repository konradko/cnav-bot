import logging.config
import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

_, HOSTNAME, _, _, MACHINE = os.uname()
RUNNING_ON_PI = (
    HOSTNAME.startswith('raspberrypi') and MACHINE.startswith('arm')
)


# Drivers #####################################################################

# Driver libs can only be installed on RPi
if RUNNING_ON_PI:
    from pi2go import pi2go  # noqa
    BOT_DRIVER = pi2go

    import bluetooth  # noqa
    BLUETOOTH_DRIVER = bluetooth._bluetooth

    from ibeaconscanner import blescan  # noqa
    IBEACON_SCANNER = blescan

    import picamera  # noqa
    CAMERA = picamera
else:
    BOT_DRIVER = None
    BLUETOOTH_DRIVER = None
    IBEACON_SCANNER = None
    CAMERA = None


# Bluetooth ###################################################################

BLUETOOTH_INIT_SCRIPT = os.path.join(
    PROJECT_ROOT, '..', 'config', 'bluetooth.sh'
)
# In seconds
BLUETOOTH_SCAN_INTERVAL = int(os.getenv('BLUETOOTH_SCAN_INTERVAL', 1))

# Camera ###################################################################
CAMERA_INTERVAL = int(os.getenv('CAMERA_INTERVAL', 1))
CAMERA_RESOLUTION_X = int(os.getenv('CAMERA_RESOLUTION_X', 640))
CAMERA_RESOLUTION_Y = int(os.getenv('CAMERA_RESOLUTION_Y', 480))
CAMERA_RESOLUTION = (CAMERA_RESOLUTION_X, CAMERA_RESOLUTION_Y)

# Bot modes ###################################################################

# 'wander' (roam freely) or 'follow' (follow line)
BOT_MODE_WANDER = 'wander'
BOT_MODE_FOLLOW = 'follow'
BOT_MODE_FOLLOW_AVOID = 'follow-avoid'
BOT_MODE_DIRECTION = 'direction'
BOT_MODE = os.getenv('BOT_MODE', BOT_MODE_WANDER)
BOT_IN_WANDER_MODE = False
BOT_IN_FOLLOW_MODE = False
BOT_IN_FOLLOW_AVOID_MODE = False
BOT_MODE_DIRECTION_MODE = False

if BOT_MODE == BOT_MODE_WANDER:
    BOT_IN_WANDER_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW:
    BOT_IN_FOLLOW_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW_AVOID:
    BOT_IN_FOLLOW_AVOID_MODE = True
elif BOT_MODE == BOT_MODE_DIRECTION:
    BOT_MODE_DIRECTION_MODE = True

BOT_WAIT_FOR_BUTTON_PRESS = os.getenv('BOT_WAIT_FOR_BUTTON_PRESS', 'true')
if BOT_WAIT_FOR_BUTTON_PRESS == 'false':
    BOT_WAIT_FOR_BUTTON_PRESS = False
else:
    BOT_WAIT_FOR_BUTTON_PRESS = True


# Defaults ####################################################################

# Must be between 0 and 100
BOT_DEFAULT_SPEED = int(os.getenv('BOT_DEFAULT_SPEED', 30))
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)
BOT_DEFAULT_MAX_DISTANCE = int(os.getenv('BOT_DEFAULT_MAX_DISTANCE', 10))
BOT_DEFAULT_DIRECTION = int(os.getenv('BOT_DEFAULT_DIRECTION', 180))
BOT_DIRECTION_TOLERANCE = int(os.getenv('BOT_DIRECTION_TOLERANCE', 180))

# Logging #####################################################################

BOT_LOG_PATH = os.environ.get('BOT_LOG_PATH', '/tmp/cnavbot.log')
SENTRY_DSN = os.environ.get('SENTRY_DSN')

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'rotating_file': {
            'class': 'zmqservices.utils.MultiprocessingRotatingFileHandler',
            'filename': BOT_LOG_PATH,
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'default',
            'level': logging.INFO,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': logging.DEBUG,
        },
    },
    'root': {
        'handlers': [
            'rotating_file',
            'console',
        ],
        'level': logging.DEBUG,
    },
})

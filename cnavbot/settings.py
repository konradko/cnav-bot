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
    from pi2go import pi2go
    BOT_DRIVER = pi2go

    import bluetooth
    BLUETOOTH_DRIVER = bluetooth._bluetooth

    from ibeaconscanner import blescan
    IBEACON_SCANNER = blescan

    import picamera
    CAMERA = picamera
else:
    BOT_DRIVER = None
    BLUETOOTH_DRIVER = None
    IBEACON_SCANNER = None
    CAMERA = None


# Bluetooth ###################################################################
BLUETOOTH_ENABLED = os.getenv('BLUETOOTH_ENABLED', 'false')
if BLUETOOTH_ENABLED == 'true':
    BLUETOOTH_ENABLED = True
else:
    BLUETOOTH_ENABLED = False

# In seconds
BLUETOOTH_SCAN_INTERVAL = int(os.getenv('BLUETOOTH_SCAN_INTERVAL', 1))


# Camera ###################################################################
CAMERA_ENABLED = os.getenv('CAMERA_ENABLED', 'false')
if CAMERA_ENABLED == 'true':
    CAMERA_ENABLED = True
else:
    CAMERA_ENABLED = False

CAMERA_INTERVAL = int(os.getenv('CAMERA_INTERVAL', 1))
CAMERA_RESOLUTION_X = int(os.getenv('CAMERA_RESOLUTION_X', 640))
CAMERA_RESOLUTION_Y = int(os.getenv('CAMERA_RESOLUTION_Y', 480))
CAMERA_RESOLUTION = (CAMERA_RESOLUTION_X, CAMERA_RESOLUTION_Y)


# cnav-sense ##################################################################
CNAV_SENSE_ENABLED = os.getenv('CNAV_SENSE_ENABLED', 'true')
if CNAV_SENSE_ENABLED == 'true':
    CNAV_SENSE_ENABLED = True
else:
    CNAV_SENSE_ENABLED = False

# must be set individually for each bot via resin.io device env vars
if CNAV_SENSE_ENABLED:
    CNAV_SENSE_ADDRESS = os.getenv('CNAV_SENSE_ADDRESS')


# Bot modes ###################################################################
BOT_ENABLED = os.getenv('BOT_ENABLED', 'true')
if BOT_ENABLED == 'true':
    BOT_ENABLED = True
else:
    BOT_ENABLED = False

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

BOT_WAIT_FOR_BUTTON_PRESS = os.getenv(
    'BOT_WAIT_FOR_BUTTON_PRESS', 'true'
)
if BOT_WAIT_FOR_BUTTON_PRESS == 'true':
    BOT_WAIT_FOR_BUTTON_PRESS = True
else:
    BOT_WAIT_FOR_BUTTON_PRESS = False


# Defaults ####################################################################

# Must be between 0 and 100
BOT_DEFAULT_SPEED = int(os.getenv('BOT_DEFAULT_SPEED', 30))
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)
BOT_DEFAULT_MAX_DISTANCE = int(os.getenv('BOT_DEFAULT_MAX_DISTANCE', 10))
BOT_DIRECTION_TOLERANCE = int(os.getenv('BOT_DIRECTION_TOLERANCE', 180))


# Logging #####################################################################

BOT_LOG_PATH = os.environ.get('BOT_LOG_PATH', '/tmp/cnavbot.log')
SENTRY_DSN = os.environ.get('SENTRY_DSN')

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'sentry': {
            'format': (
                '[%(asctime)s][%(levelname)s] %(name)s '
                '%(filename)s:%(funcName)s:%(lineno)d | %(message)s'
            ),
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'rotating_file': {
            'class': 'zmqservices.utils.MultiprocessingRotatingFileHandler',
            'filename': BOT_LOG_PATH,
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'default',
            'level': 'INFO',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'sentry': {
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
            'level': 'ERROR',
            'formatter': 'sentry',
        },
        'papertrail': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'default',
            'address': (
                os.getenv('PAPERTRAIL_HOST'), os.getenv('PAPERTRAIL_PORT')
            ),
            'level': 'INFO',
        }
    },
    'root': {
        'handlers': [
            'rotating_file',
            'console',
            'sentry',
            'papertrail',
        ],
        'level': 'DEBUG',
    },
})

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

    import cv2
    CV2 = cv2

    import numpy
    NUMPY = numpy
else:
    BOT_DRIVER = None
    BLUETOOTH_DRIVER = None
    IBEACON_SCANNER = None
    CAMERA = None
    CV2 = None
    NUMPY = None


# Bluetooth ###################################################################
BLUETOOTH_ENABLED = os.getenv('BLUETOOTH_ENABLED', 'false')
if BLUETOOTH_ENABLED == 'true':
    BLUETOOTH_ENABLED = True
else:
    BLUETOOTH_ENABLED = False

# In seconds
BLUETOOTH_SCAN_INTERVAL = int(os.getenv('BLUETOOTH_SCAN_INTERVAL', 1))


# Beacons #####################################################################

BEACON_ONE_ID = os.getenv(
    'BEACON_ONE_ID', 'e2c56db5dffb48d2b060d0f5a71096e1'
)
BEACON_TWO_ID = os.getenv(
    'BEACON_TWO_ID', 'e2c56db5dffb48d2b060d0f5a71096e2'
)
BEACON_THREE_ID = os.getenv(
    'BEACON_THREE_ID', 'e2c56db5dffb48d2b060d0f5a71096e3'
)
BEACONS = [
    BEACON_ONE_ID,
    BEACON_TWO_ID,
    BEACON_THREE_ID
]


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
FILE_MESSAGE_STORAGE_PATH = os.getenv('FILE_MESSAGE_STORAGE_PATH', '/tmp/')

# Target following ############################################################

BOT_SEARCH_FOR_TARGET = os.getenv('BOT_SEARCH_FOR_TARGET', 'true')
if BOT_SEARCH_FOR_TARGET == 'true':
    BOT_SEARCH_FOR_TARGET = True
else:
    BOT_SEARCH_FOR_TARGET = False

# Smallest target to move towards
TARGET_MINIMUM_AREA = int(os.getenv('MINIMUM_TARGET_AREA', 100))

TARGET_COLOUR_LOW_H = int(os.getenv('TARGET_COLOUR_LOW_H', 115))
TARGET_COLOUR_LOW_S = int(os.getenv('TARGET_COLOUR_LOW_S', 127))
TARGET_COLOUR_LOW_V = int(os.getenv('TARGET_COLOUR_LOW_V', 64))

TARGET_COLOUR_LOW = (
    TARGET_COLOUR_LOW_H, TARGET_COLOUR_LOW_S, TARGET_COLOUR_LOW_V
)

TARGET_COLOUR_HIGH_H = int(os.getenv('TARGET_COLOUR_HIGH_H', 125))
TARGET_COLOUR_HIGH_S = int(os.getenv('TARGET_COLOUR_HIGH_S', 255))
TARGET_COLOUR_HIGH_V = int(os.getenv('TARGET_COLOUR_HIGH_V', 255))

TARGET_COLOUR_HIGH = (
    TARGET_COLOUR_HIGH_H, TARGET_COLOUR_HIGH_S, TARGET_COLOUR_HIGH_V
)

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
BOT_MODE_FOLLOW_DIRECTION_AND_LINE = 'direction-line'
BOT_MODE_FOLLOW_CAMERA_TARGET = 'follow-camera-target'
BOT_MODE = os.getenv('BOT_MODE', BOT_MODE_WANDER)
BOT_IN_WANDER_MODE = False
BOT_IN_FOLLOW_MODE = False
BOT_IN_FOLLOW_AVOID_MODE = False
BOT_IN_FOLLOW_DIRECTION_MODE = False
BOT_IN_FOLLOW_CAMERA_TARGET_MODE = False
BOT_IN_FOLLOW_DIRECTION_AND_LINE_MODE = False

if BOT_MODE == BOT_MODE_WANDER:
    BOT_IN_WANDER_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW:
    BOT_IN_FOLLOW_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW_AVOID:
    BOT_IN_FOLLOW_AVOID_MODE = True
elif BOT_MODE == BOT_MODE_DIRECTION:
    BOT_MODE_DIRECTION_MODE = True
    CNAV_SENSE_ENABLED = True
elif BOT_MODE == BOT_MODE_FOLLOW_CAMERA_TARGET:
    BOT_IN_FOLLOW_CAMERA_TARGET_MODE = True
    CAMERA_ENABLED = True
elif BOT_MODE == BOT_MODE_FOLLOW_DIRECTION_AND_LINE:
    BOT_IN_FOLLOW_DIRECTION_AND_LINE_MODE = True
    CNAV_SENSE_ENABLED = True

BOT_WAIT_FOR_BUTTON_PRESS = os.getenv(
    'BOT_WAIT_FOR_BUTTON_PRESS', 'true'
)
if BOT_WAIT_FOR_BUTTON_PRESS == 'true':
    BOT_WAIT_FOR_BUTTON_PRESS = True
else:
    BOT_WAIT_FOR_BUTTON_PRESS = False


# Defaults ####################################################################

# Must be between 0 and 100
BOT_DEFAULT_SPEED = int(os.getenv('BOT_DEFAULT_SPEED', 50))
BOT_DEFAULT_FORWARD_STEPS = int(os.getenv('BOT_DEFAULT_FORWARD_STEPS', 3))
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)
BOT_DEFAULT_MAX_DISTANCE = int(os.getenv('BOT_DEFAULT_MAX_DISTANCE', 10))
BOT_DIRECTION_TOLERANCE = int(os.getenv('BOT_DIRECTION_TOLERANCE', 10))


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
                os.getenv('PAPERTRAIL_HOST'),
                int(os.getenv('PAPERTRAIL_PORT', 0))
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
        'propagate': True,
    },
})

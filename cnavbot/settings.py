import logging.config
import os

from raven import Client


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
BOT_MODE = os.getenv('BOT_MODE', BOT_MODE_WANDER)
BOT_IN_WANDER_MODE = False
BOT_IN_FOLLOW_MODE = False
BOT_IN_FOLLOW_AVOID_MODE = False

if BOT_MODE == BOT_MODE_WANDER:
    BOT_IN_WANDER_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW:
    BOT_IN_FOLLOW_MODE = True
elif BOT_MODE == BOT_MODE_FOLLOW_AVOID:
    BOT_IN_FOLLOW_AVOID_MODE = True

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


# Logging #####################################################################

BOT_LOG_PATH = os.environ.get('BOT_LOG_PATH', '/tmp/cnavbot.log')
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
SENTRY_CLIENT = Client(SENTRY_DSN) if SENTRY_DSN else None

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
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

# Messaging ###################################################################

LOCAL_PUBLISHER_ADDRESS = 'tcp://localhost:{port}'
PUBLISHER_PORT_ADDRESS = 'tcp://*:{port}'

BLUETOOTH_PUBLISHER_TOPIC = '{}.bluetooth'.format(
    BOT_DEFAULT_NAME.replace(' ', '')
)
BLUETOOTH_PORT = int(os.getenv('BLUETOOTH_PORT', 48630))
LOCAL_BLUETOOTH_PUBLISHER_ADDRESS = LOCAL_PUBLISHER_ADDRESS.format(
    port=BLUETOOTH_PORT
)
BLUETOOTH_PUBLISHER_PORT = PUBLISHER_PORT_ADDRESS.format(
    port=BLUETOOTH_PORT
)

FILE_MESSAGE_STORAGE_PATH = os.getenv('FILE_MESSAGE_STORAGE_PATH', '/tmp')
if not os.path.exists(FILE_MESSAGE_STORAGE_PATH):
    os.makedirs(FILE_MESSAGE_STORAGE_PATH)

CAMERA_PUBLISHER_TOPIC = '{}.camera'.format(
    BOT_DEFAULT_NAME.replace(' ', '')
)
CAMERA_PORT = int(os.getenv('CAMERA_PORT', 48631))
LOCAL_CAMERA_PUBLISHER_ADDRESS = LOCAL_PUBLISHER_ADDRESS.format(
    port=CAMERA_PORT
)
CAMERA_PUBLISHER_PORT = PUBLISHER_PORT_ADDRESS.format(
    port=CAMERA_PORT
)

BOT_PORT = int(os.getenv('BOT_PORT', 48632))
LOCAL_BOT_PUBLISHER_ADDRESS = LOCAL_PUBLISHER_ADDRESS.format(
    port=BOT_PORT
)
BOT_PUBLISHER_PORT = PUBLISHER_PORT_ADDRESS.format(
    port=BOT_PORT
)

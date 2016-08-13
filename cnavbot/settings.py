import os

from raven import Client


_, HOSTNAME, _, _, MACHINE = os.uname()
RUNNING_ON_PI = (
    HOSTNAME.startswith('raspberrypi') and MACHINE.startswith('arm')
)

# RPi.GPIO python lib required by pi2go can only be imported on a Raspberry Pi
if RUNNING_ON_PI:
    from pi2go import pi2go  # noqa
    BOT_DRIVER = pi2go
else:
    BOT_DRIVER = None

# Must be between 0 and 100
BOT_DEFAULT_SPEED = int(os.getenv('BOT_DEFAULT_SPEED', 50))
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
SENTRY_CLIENT = Client(SENTRY_DSN) if SENTRY_DSN else None

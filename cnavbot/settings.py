import os
import platform


_, HOSTNAME, _, _, MACHINE = os.uname()
RUNNING_ON_PI = (
    HOSTNAME.startswith('raspberrypi') and MACHINE.startswith('arm')
)

# RPi.GPIO python lib required by pi2go can only be imported on a Raspberry Pi
if RUNNING_ON_PI:
    from pi2go import pi2go
    BOT_DRIVER = pigo
else:
    from mock import Mock
    BOT_DRIVER = Mock()

# Must be between 0 and 100
BOT_DEFAULT_SPEED = os.getenv('BOT_DEFAULT_SPEED', 50)
BOT_DEFAULT_NAME = os.getenv('BOT_DEFAULT_NAME', HOSTNAME)


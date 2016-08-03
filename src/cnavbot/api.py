from pi2go import pi2go

from cnavbot import settings


class Motors(object):

    def __init__(self, speed=None, *args, **kwargs):
        self.speed = speed or settings.BOT_DEFAULT_SPEED
        self.validate_speed(self.speed)

    @staticmethod
    def validate_speed(speed):
        if not (1 <= speed <= 100):
            raise Exception(
                "Invalid speed value '{}', must be between 1 an 100".format(
                    speed
                )
            )

    def forward(self):
        """Sets both motors to go forward"""
        pi2go.forward(self.speed)

    def reverse(self):
        """Sets both motors to reverse"""
        pi2go.reverse(self.speed)

    def spin_left(self):
        """Sets motors to turn opposite directions for left spin"""
        pi2go.spinLeft(self.speed)

    def spin_right(self):
        """Sets motors to turn opposite directions for right spin"""
        pi2go.spinRight(self.speed)

    def step_forward(self, steps):
        """Moves forward specified number of steps"""
        pi2go.stepForward(self.speed, steps)

    def step_reverse(self, steps):
        """Moves backward specified number of steps"""
        pi2go.stepReverse(self.speed, steps)

    def step_spin_left(self, steps):
        """Spins left specified number of steps"""
        pi2go.stepSpinL(self.speed, steps)

    def step_spin_right(self, steps):
        """Spins right specified number of steps"""
        pi2go.stepSpinR(self.speed, steps)

    @staticmethod
    def stop():
        pi2go.stop()


class Lights(object):
    led_numbers = (1, 2, 3, 4)

    @staticmethod
    def set_led_rbg(led_number, red, blue, green):
        """Spins right specified number of steps"""
        pi2go.setLED(led_number, red, green, blue)

    def set_all_leds_rbg(self, red, blue, green):
        """Spins right specified number of steps"""
        for led_number in self.led_numbers:
            pi2go.setLED(led_number, red, green, blue)


class Obstacle(object):

    @staticmethod
    def left():
        """Returns true if there is an obstacle to the left"""
        return pi2go.irLeft()

    @staticmethod
    def right():
        """Returns true if there is an obstacle to the right"""
        return pi2go.irRight()

    @staticmethod
    def front():
        """Returns true if there is an obstacle in front"""
        return pi2go.irCentre()

    @staticmethod
    def front_distance():
        """
        Returns the distance in cm to the nearest reflecting object
        in front of the bot
        """
        return pi2go.getDistance()

    @staticmethod
    def any():
        """Returns true if there is any obstacle"""
        return pi2go.irAll()


class LineSensor(object):
    # irLeftLine(): Returns state of Left IR Line sensor

    @staticmethod
    def left():
        """Returns the state of the left line sensor"""
        return pi2go.irLeftLine()

    @staticmethod
    def right():
        """Returns the state of the right line sensor"""
        return pi2go.irRightLine()


class Bot(object):

    def __init__(self, name=None, speed=None, *args, **kwargs):
        self.name = name or settings.BOT_DEFAULT_NAME
        self.validate_speed(speed)
        self.motors = Motors(speed)
        self.lights = Lights()
        self.obstacle = Obstacle()
        self.line_sensor = LineSensor()
        pi2go.init()

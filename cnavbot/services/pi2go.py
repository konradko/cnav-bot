import time
import logging

from cnavbot import settings


logger = logging.getLogger()


class Driver(object):

    def __init__(self, *args, **kwargs):
        self.driver = kwargs.pop('driver', settings.BOT_DRIVER)


class Motors(Driver):

    def __init__(self, speed=None, *args, **kwargs):
        super(Motors, self).__init__(*args, **kwargs)
        self.speed = kwargs.pop('speed', settings.BOT_DEFAULT_SPEED)
        self.validate_speed(self.speed)
        logger.info('Speed set to {}'.format(self.speed))

    @staticmethod
    def validate_speed(speed):
        if not (1 <= speed <= 100):
            raise Exception(
                "Invalid speed value '{}', must be between 1 an 100".format(
                    speed
                )
            )

    def forward(self, steps=None):
        """Sets both motors to go forward"""
        logger.debug('Going forward')
        self.driver.forward(self.speed)

        if steps:
            self.keep_running(steps)

    def reverse(self, steps=None):
        """Sets both motors to reverse"""
        logger.debug('Reversing')
        self.driver.reverse(self.speed)

        if steps:
            self.keep_running(steps)

    def left(self, steps=None):
        """Sets motors to turn opposite directions for left spin"""
        logger.debug('Spinning left')
        self.driver.spinLeft(self.speed)

        if steps:
            self.keep_running(steps)

    def right(self, steps=None):
        """Sets motors to turn opposite directions for right spin"""
        logger.debug('Spinning right')
        self.driver.spinRight(self.speed)

        if steps:
            self.keep_running(steps)

    def keep_running(self, steps):
        logger.debug('Keeping running for {} steps'.format(steps))
        time.sleep(0.1 * steps)
        self.stop()

    def stop(self):
        logger.debug('Stopping')
        self.driver.stop()


class Lights(Driver):
    led_numbers = (1, 2, 3, 4)

    def validate_led_number(self, led_number):
        if not(led_number in self.led_numbers):
            raise Exception(
                "Invalid led number '{}', must be in {}".format(
                    led_number,
                    self.led_numbers
                )
            )

    def set_led_rbg(self, led_number, red, blue, green):
        """Spins right specified number of steps"""
        self.validate_led_number(led_number)
        logger.debug('Setting LED {} to red: {}, green: {}. blue: {}'.format(
            led_number, red, green, blue
        ))
        self.driver.setLED(led_number, red, green, blue)

    def set_all_leds_rbg(self, red, blue, green):
        """Spins right specified number of steps"""
        for led_number in self.led_numbers:
            self.driver.setLED(led_number, red, green, blue)


class ObstacleSensor(Driver):

    def __init__(self, *args, **kwargs):
        super(ObstacleSensor, self).__init__(*args, **kwargs)
        self.max_distance = kwargs.pop(
            'max_distance', settings.BOT_DEFAULT_MAX_DISTANCE
        )
        logger.info('Max distance set to {}'.format(self.max_distance))

    def left(self):
        """Returns true if there is an obstacle to the left"""
        obstacle = self.driver.irLeft()
        logger.debug('Left obstacle: {}'.format(obstacle))
        return obstacle

    def right(self):
        """Returns true if there is an obstacle to the right"""
        obstacle = self.driver.irRight()
        logger.debug('Right obstacle: {}'.format(obstacle))
        return obstacle

    def front(self):
        """Returns true if there is an obstacle in front"""
        obstacle = self.driver.irCentre()
        logger.debug('Front obstacle: {}'.format(obstacle))
        return obstacle

    def front_close(self):
        front_close = self.distance() <= self.max_distance
        logger.debug('Front obstacle close: {}'.format(front_close))
        return front_close

    def distance(self):
        """
        Returns the distance in cm to the nearest reflecting object
        in front of the bot
        """
        distance = self.driver.getDistance()
        logger.debug('Distance: {}'.format(distance))
        return distance

    def any(self):
        """Returns true if there is any obstacle"""
        any_obstacle = self.driver.irAll()
        logger.debug('Any obstacle: {}'.format(any_obstacle))
        return any_obstacle


class LineSensor(Driver):

    def left(self):
        """Returns True if left line sensor detected dark line"""
        left = not self.driver.irLeftLine()
        logger.debug('Left line detected: {}'.format(left))
        return left

    def right(self):
        """Returns True if right line sensor detected dark line"""
        right = not self.driver.irRightLine()
        logger.debug('Right line detected: {}'.format(right))
        return right

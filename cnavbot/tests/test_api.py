from unittest import TestCase

import mock
import pytest

from cnavbot import api, settings


class Test(TestCase):
    bot = api.Bot(driver=mock.Mock())

class TestMotors(Test):

    motors = api.Motors(driver=mock.Mock())
    steps = 5

    def test_validate_speed(self):
        with pytest.raises(Exception) as excinfo:
            api.Motors.validate_speed(0)
        assert excinfo.value.message == (
            "Invalid speed value '0', must be between 1 an 100"
        )

        with pytest.raises(Exception) as excinfo:
            api.Motors.validate_speed(101)
        assert excinfo.value.message == (
            "Invalid speed value '101', must be between 1 an 100"
        )

    def test_forward(self):
        self.motors.forward()

        self.motors.driver.forward.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_reverse(self):
        self.motors.reverse()

        self.motors.driver.reverse.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_spin_left(self):
        self.motors.spin_left()

        self.motors.driver.spinLeft.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_spin_right(self):
        self.motors.spin_right()

        self.motors.driver.spinRight.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_step_forward(self):
        self.motors.step_forward(steps=self.steps)

        self.motors.driver.stepForward.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_reverse(self):
        self.motors.step_reverse(steps=self.steps)

        self.motors.driver.stepReverse.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_spin_left(self):
        self.motors.step_spin_left(steps=self.steps)

        self.motors.driver.stepSpinL.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_spin_right(self):
        self.motors.step_spin_right(steps=self.steps)

        self.motors.driver.stepSpinR.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_stop(self):
        self.motors.stop()

        self.motors.driver.stop.assert_called_once()


# class TestLights(Test):

#     def test_set_led_rbg(self):
#         """Spins right specified number of steps"""
#         driver.setLED(led_number, red, green, blue)

#     def test_set_all_leds_rbg(self):
#         """Spins right specified number of steps"""
#         for led_number in self.led_numbers:
#             driver.setLED(led_number, red, green, blue)


# class TestObstacle(Test):

#     def test_left(self):
#         """Returns true if there is an obstacle to the left"""
#         return driver.irLeft()

#     def test_right(self):
#         """Returns true if there is an obstacle to the right"""
#         return driver.irRight()

#     def test_front(self):
#         """Returns true if there is an obstacle in front"""
#         return driver.irCentre()

#     def test_front_distance(self):
#         """
#         Returns the distance in cm to the nearest reflecting object
#         in front of the bot
#         """
#         return driver.getDistance()

#     def test_any(self):
#         """Returns true if there is any obstacle"""
#         return driver.irAll()


# class TestLineSensor(Test):
#     # irLeftLine(): Returns state of Left IR Line sensor

#     def test_left(self):
#         """Returns the state of the left line sensor"""
#         return driver.irLeftLine()

#     def test_right(self):
#         """Returns the state of the right line sensor"""
#         return driver.irRightLine()


# class TestBot(Test):

#     def __init__(self):
#         self.name = name or settings.BOT_DEFAULT_NAME
#         self.speed = speed or settings.BOT_DEFAULT_SPEED
#         self.validate_speed(self.speed)
#         self.motors = Motors()
#         self.lights = Lights()
#         self.obstacle = Obstacle()
#         self.line_sensor = LineSensor()
#         driver.init()


from unittest import TestCase

import mock
import pytest

from ..cnavbot import api, settings


@mock.patch('pi2go.pi2go')
class Test(TestCase):
    pass

    bot = api.Bot()

    lights = api.Lights()
    obstacle = api.Obstacle()
    line_sensor = api.LineSensor()


@mock.patch('pi2go.pi2go')
class TestMotors(Test):

    motors = api.Motors()
    steps = 5

    def test_validate_speed(self, pi2go_mock):
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

    def test_forward(self, pi2go_mock):
        self.motors.forward()

        pi2go_mock.forward.assert_called_once_with(
            speed=settings.BOT_DEFAULT_SPEED
        )

    def test_reverse(self, pi2go_mock):
        self.motors.reverse()

        pi2go_mock.reverse.assert_called_once_with(
            speed=settings.BOT_DEFAULT_SPEED
        )

    def test_spin_left(self, pi2go_mock):
        self.motors.spin_left()

        pi2go_mock.spinLeft.assert_called_once_with(
            speed=settings.BOT_DEFAULT_SPEED
        )

    def test_spin_right(self, pi2go_mock):
        self.motors.spin_right()

        pi2go_mock.spinRight.assert_called_once_with(
            speed=settings.BOT_DEFAULT_SPEED
        )

    def test_step_forward(self, pi2go_mock):
        self.motors.step_forward(steps=self.steps)

        pi2go_mock.stepForward.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_reverse(self, pi2go_mock):
        self.motors.step_reverse(steps=self.steps)

        pi2go_mock.stepReverse.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_spin_left(self, pi2go_mock):
        self.motors.step_spin_left(steps=self.steps)

        pi2go_mock.stepSpinL.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_step_spin_right(self, pi2go_mock):
        self.motors.step_spin_right(steps=self.steps)

        pi2go_mock.stepSpinR.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED, self.steps
        )

    def test_stop(self, pi2go_mock):
        self.motors.stop()

        pi2go_mock.stepSpinR.assert_called_once()


class TestLights(Test):

    def test_set_led_rbg(self, pi2go_mock):
        """Spins right specified number of steps"""
        pi2go.setLED(led_number, red, green, blue)

    def test_set_all_leds_rbg(self, pi2go_mock):
        """Spins right specified number of steps"""
        for led_number in self.led_numbers:
            pi2go.setLED(led_number, red, green, blue)


class TestObstacle(Test):

    def test_left(self, pi2go_mock):
        """Returns true if there is an obstacle to the left"""
        return pi2go.irLeft()

    def test_right(self, pi2go_mock):
        """Returns true if there is an obstacle to the right"""
        return pi2go.irRight()

    def test_front(self, pi2go_mock):
        """Returns true if there is an obstacle in front"""
        return pi2go.irCentre()

    def test_front_distance(self, pi2go_mock):
        """
        Returns the distance in cm to the nearest reflecting object
        in front of the bot
        """
        return pi2go.getDistance()

    def test_any(self, pi2go_mock):
        """Returns true if there is any obstacle"""
        return pi2go.irAll()


class TestLineSensor(Test):
    # irLeftLine(): Returns state of Left IR Line sensor

    def test_left(self, pi2go_mock):
        """Returns the state of the left line sensor"""
        return pi2go.irLeftLine()

    def test_right(self, pi2go_mock):
        """Returns the state of the right line sensor"""
        return pi2go.irRightLine()


class TestBot(Test):

    def __init__(self, pi2go_mock):
        self.name = name or settings.BOT_DEFAULT_NAME
        self.speed = speed or settings.BOT_DEFAULT_SPEED
        self.validate_speed(self.speed)
        self.motors = Motors()
        self.lights = Lights()
        self.obstacle = Obstacle()
        self.line_sensor = LineSensor()
        pi2go.init()


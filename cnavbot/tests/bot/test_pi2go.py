from unittest import TestCase

import mock
import pytest

from cnavbot import settings
from cnavbot.bot import pi2go


class TestMotors(TestCase):

    def setUp(self):
        self.motors = pi2go.Motors(driver=mock.Mock())
        self.motors.keep_running = mock.Mock()
        self.steps = 5

    def test_validate_speed(self):
        with pytest.raises(Exception) as excinfo:
            pi2go.Motors.validate_speed(0)
        assert excinfo.value.message == (
            "Invalid speed value '0', must be between 1 an 100"
        )

        with pytest.raises(Exception) as excinfo:
            pi2go.Motors.validate_speed(101)
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
        self.motors.left()

        self.motors.driver.spinLeft.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_spin_right(self):
        self.motors.right()

        self.motors.driver.spinRight.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )

    def test_step_forward(self):
        self.motors.forward(steps=self.steps)

        self.motors.driver.forward.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )
        self.motors.keep_running.assert_called_with(self.steps)

    def test_step_reverse(self):
        self.motors.reverse(steps=self.steps)

        self.motors.driver.reverse.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )
        self.motors.keep_running.assert_called_with(self.steps)

    def test_step_spin_left(self):
        self.motors.left(steps=self.steps)

        self.motors.driver.spinLeft.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )
        self.motors.keep_running.assert_called_with(self.steps)

    def test_step_spin_right(self):
        self.motors.right(steps=self.steps)

        self.motors.driver.spinRight.assert_called_once_with(
            settings.BOT_DEFAULT_SPEED
        )
        self.motors.keep_running.assert_called_with(self.steps)

    def test_stop(self):
        self.motors.stop()

        self.motors.driver.stop.assert_called_once()


class TestLights(TestCase):
    lights = pi2go.Lights(driver=mock.Mock())

    def test_validate_led_number(self):
        with pytest.raises(Exception) as excinfo:
            self.lights.validate_led_number(555)
        assert excinfo.value.message == (
            "Invalid led number '555', must be in {}".format(
                self.lights.led_numbers
            )
        )

    def test_set_led_rbg(self):
        self.lights.set_led_rbg(1, 233, 233, 233)

        self.lights.driver.setLED.assert_called_with(1, 233, 233, 233)

    def test_set_all_leds_rbg(self):
        self.lights.set_all_leds_rbg(255, 255, 255)
        for led_number in self.lights.led_numbers:
            self.lights.driver.setLED.assert_any_call(
                led_number, 255, 255, 255
            )


class TestObstacleSensor(TestCase):
    obstacle_sensor = pi2go.ObstacleSensor(driver=mock.Mock())

    def test_left(self):
        self.obstacle_sensor.left()

        self.obstacle_sensor.driver.irLeft.assert_called_once()

    def test_right(self):
        self.obstacle_sensor.right()

        self.obstacle_sensor.driver.irRight.assert_called_once()

    def test_front(self):
        self.obstacle_sensor.front()

        self.obstacle_sensor.driver.irCentre.assert_called_once()

    def test_distance(self):
        self.obstacle_sensor.distance()

        self.obstacle_sensor.driver.getDistance.assert_called_once()

    def test_any(self):
        self.obstacle_sensor.any()

        self.obstacle_sensor.driver.irAll()


class TestLineSensor(TestCase):
    line_sensor = pi2go.LineSensor(driver=mock.Mock())

    def test_left(self):
        self.line_sensor.left()

        self.line_sensor.driver.irLeftLine.assert_called_once()

    def test_right(self):
        self.line_sensor.right()

        self.line_sensor.driver.irRightLine.assert_called_once()

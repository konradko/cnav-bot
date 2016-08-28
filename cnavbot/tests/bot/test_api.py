from unittest import TestCase

import mock

from cnavbot import settings
from cnavbot.bot import api


class TestBot(TestCase):

    def setUp(self):
        with mock.patch('cnavbot.settings.BLUETOOTH_DRIVER'):
            with mock.patch('cnavbot.settings.IBEACON_SCANNER'):
                with mock.patch('cnavbot.settings.CAMERA'):
                    with mock.patch('cnavbot.settings.BOT_DRIVER'):
                        self.bot = api.Bot(publisher=mock.Mock())
                        self.bot.motors.keep_running = mock.Mock()

    def test__init__(self):
        assert self.bot.name == settings.BOT_DEFAULT_NAME
        assert self.bot.motors
        assert self.bot.lights
        assert self.bot.obstacle_sensor
        assert self.bot.line_sensor
        self.bot.driver.init.assert_called_once()

    def test_cleanup(self):
        self.bot.cleanup()

        self.bot.driver.cleanup.assert_called_once()

    def test_avoid_left_obstacle(self):
        self.bot.driver.irLeft.side_effect = [True, False]

        self.bot.avoid_left_obstacle()

        self.bot.driver.spinRight.assert_called_once_with(
            self.bot.motors.speed
        )
        self.bot.motors.keep_running.assert_called_once()

    def test_avoid_right_obstacle(self):
        self.bot.driver.irRight.side_effect = [True, False]

        self.bot.avoid_right_obstacle()

        self.bot.driver.spinLeft.assert_called_once_with(
            self.bot.motors.speed
        )
        self.bot.motors.keep_running.assert_called_once()

    def test_avoid_front_obstacle_right_free(self):
        self.bot.driver.irCentre.side_effect = [True, False]
        self.bot.driver.irRight.return_value = False
        self.bot.driver.irLeft.side_effect = [True, False]

        self.bot.avoid_front_obstacle()

        self.bot.driver.spinRight.assert_called_once_with(
            self.bot.motors.speed
        )

        self.bot.motors.keep_running.assert_called_once()

    def test_avoid_front_obstacle_left_free(self):
        self.bot.driver.irCentre.side_effect = [True, False]
        self.bot.driver.irRight.return_value = True
        self.bot.driver.irLeft.return_value = False

        self.bot.avoid_front_obstacle()

        self.bot.driver.spinLeft.assert_called_once_with(
            self.bot.motors.speed
        )
        self.bot.motors.keep_running.assert_called_once()

    def test_avoid_front_left_right_obstacles(self):
        self.bot.driver.irCentre.side_effect = [True, False]
        self.bot.driver.irRight.return_value = True
        self.bot.driver.irLeft.return_value = True
        self.bot.obstacle_sensor.driver.getDistance.side_effect = [
            settings.BOT_DEFAULT_MAX_DISTANCE - 1,
            settings.BOT_DEFAULT_MAX_DISTANCE + 1,
        ]

        self.bot.avoid_front_obstacle()

        self.bot.driver.reverse.assert_called_once_with(
            self.bot.motors.speed
        )
        self.bot.motors.keep_running.assert_called_once()

    def test_switch_pressed(self):
        self.bot.driver.getSwitch.return_value = True
        return_value = self.bot.switch_pressed

        assert return_value
        self.bot.driver.getSwitch.assert_called_once_with()

    @mock.patch('time.sleep')
    def test_wait_till_switch_pressed(self, time_mock):
        self.bot.driver.getSwitch.side_effect = [False, True]

        self.bot.wait_till_switch_pressed()

        self.bot.driver.getSwitch.assert_called()
        time_mock.assert_called()

    def test_distance(self):
        self.bot.distance

        self.bot.obstacle_sensor.driver.getDistance.assert_called_once()

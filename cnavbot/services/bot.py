import time

from zmqservices import services
from cnavconstants.publishers import (
    LOCAL_BOT_ADDRESS, BOT_SERVICE_PORT
)
import cnavconstants.topics

from cnavbot import settings
from cnavbot.services import bluetooth, camera, pi2go
from cnavbot.utils import logger, sentry


class Bot(services.PublisherResource):
    topics = {
        'drive': cnavconstants.topics.BOT,
    }

    # Number of steps required for 360 spin
    full_spin_steps = 44
    # Default number of steps
    steps = 2

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

        self.driver = kwargs.get('driver', settings.BOT_DRIVER)
        self.driver.init()

        self.name = kwargs.get('name', settings.BOT_DEFAULT_NAME)

        self.motors = pi2go.Motors(driver=self.driver)
        self.lights = pi2go.Lights(driver=self.driver)
        self.line_sensor = pi2go.LineSensor(driver=self.driver)
        self.obstacle_sensor = pi2go.ObstacleSensor(driver=self.driver)

        self.bluetooth = bluetooth.Service.get_subscriber()
        self.camera = camera.Service.get_subscriber()

    def run(self):
        with sentry():
            if settings.BOT_WAIT_FOR_BUTTON_PRESS:
                self.wait_till_switch_pressed()

            if settings.BOT_IN_WANDER_MODE:
                self.wander_continuously()

            elif settings.BOT_IN_FOLLOW_MODE:
                self.follow_line_continuously()

            elif settings.BOT_IN_FOLLOW_AVOID_MODE:
                self.follow_line_and_avoid_obstacles_continuously()

            self.cleanup()

    def cleanup(self):
        logger.info('Cleaning up')
        self.driver.cleanup()

    @property
    def bluetooth_scan_results(self):
        return self.bluetooth.receive().data

    @property
    def picture(self):
        return self.camera.receive().data

    @property
    def left_line(self):
        return self.line_sensor.left()

    @property
    def right_line(self):
        return self.line_sensor.right()

    @property
    def switch_pressed(self):
        switch_pressed = self.driver.getSwitch()
        if switch_pressed:
            logger.debug('Switch pressed')
        return switch_pressed

    def wait_till_switch_pressed(self):
        logger.info('Waiting for switch to be pressed...')
        while True:
            if self.switch_pressed:
                return
            else:
                time.sleep(1)

    @property
    def front_obstacle(self):
        return self.obstacle_sensor.front()

    @property
    def front_obstacle_close(self):
        return self.obstacle_sensor.front_close()

    @property
    def left_obstacle(self):
        return self.obstacle_sensor.left()

    @property
    def right_obstacle(self):
        return self.obstacle_sensor.right()

    @property
    def any_obstacle(self):
        return any((
            self.front_obstacle,
            self.left_obstacle,
            self.right_obstacle
        ))

    @property
    def distance(self):
        return self.obstacle_sensor.distance()

    def avoid_left_obstacle(self):
        step_counter = 0
        while self.left_obstacle:
            logger.debug('Avoiding left obstacle')
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid left obstacle')
                return
            self.motors.right(steps=self.steps)
            step_counter += self.steps

    def avoid_right_obstacle(self):
        step_counter = 0
        while self.right_obstacle:
            logger.debug('Avoiding right obstacle')
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid right obstacle')
                return
            self.motors.left(steps=self.steps)
            step_counter += self.steps

    def avoid_front_obstacle(self):
        while self.front_obstacle:
            logger.debug('Avoiding front obstacle')
            if not self.right_obstacle:
                self.motors.right(steps=self.steps)
            elif not self.left_obstacle:
                self.motors.left(steps=self.steps)
            else:
                while self.front_obstacle_close:
                    self.motors.reverse(steps=self.steps)

    def avoid_obstacles(self):
        while self.any_obstacle:
            logger.debug('Avoiding obstacles')
            self.avoid_front_obstacle()
            self.avoid_left_obstacle()
            self.avoid_right_obstacle()

    def wander(self):
        logger.debug('Wandering')
        self.avoid_obstacles()
        self.motors.forward()
        self.motors.keep_running(steps=self.steps)

    def wander_continuously(self):
        logger.info('Wandering...')
        while True:
            self.wander()

    def follow_line(self):
        last_left = False
        last_right = False
        if (not self.left_line) and (not self.right_line):
            self.motors.forward()
        elif self.left_line:
            last_left = True
            last_right = False
            self.motors.right(steps=1)
        elif self.right_line:
            last_right = True
            last_left = False
            self.motors.left(steps=1)
        elif self.left_line and self.right_line:
            self.reverse(steps=2)
            if last_right:
                self.motors.left(steps=2)
            if last_left:
                self.motors.right(steps=2)

    def follow_line_continuously(self):
        logger.info('Following line...')
        while True:
            self.follow_line()

    def follow_line_and_avoid_obstacles(self):
        self.avoid_obstacles()
        self.follow_line()

    def follow_line_and_avoid_obstacles_continuously(self):
        logger.info('Following line and avoiding obstacles...')
        while True:
            self.follow_line_and_avoid_obstacles()


class Service(services.PublisherService):
    name = 'bot'
    resource = Bot
    address = LOCAL_BOT_ADDRESS
    port = BOT_SERVICE_PORT


def start():
    return Service().start()


if __name__ == '__main__':
    start()

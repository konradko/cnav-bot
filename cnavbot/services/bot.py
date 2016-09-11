import time

import zmq

from zmqservices import services, pubsub, clientserver, messages
import cnavconstants.topics
import cnavconstants.publishers
import cnavconstants.servers

from cnavbot import settings
from cnavbot.services import bluetooth, camera, pi2go
from cnavbot.utils import logger, log_exceptions


class Bot(services.PublisherResource):
    topics = {
        'drive': cnavconstants.topics.BOT,
    }

    # Number of steps required for 360 spin
    full_spin_steps = 44
    # Default number of steps
    steps = 2

    # Used to set bot direction based on joystick input
    directions = {
        'up': 0,
        'down': 180,
        'left': -45,
        'right': 45,
    }

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

        if settings.CNAV_SENSE_ENABLED:
            self.setup_sense_services()

    def run(self):
        with log_exceptions():
            if settings.BOT_WAIT_FOR_BUTTON_PRESS:
                self.wait_till_switch_pressed()

            if settings.BOT_MODE_DIRECTION_MODE:
                self.drive_in_direction_continuously(
                    direction=self.wait_for_joystick_direction()
                )

            elif settings.BOT_IN_WANDER_MODE:
                self.wander_continuously()

            elif settings.BOT_IN_FOLLOW_MODE:
                self.follow_line_continuously()

            elif settings.BOT_IN_FOLLOW_AVOID_MODE:
                self.follow_line_and_avoid_obstacles_continuously()

            self.cleanup()

    @staticmethod
    def get_sense_service_address(port):
        return 'tcp://{}:{}'.format(settings.CNAV_SENSE_ADDRESS, port)

    def setup_sense_services(self):
        inertial_service = self.get_sense_service_address(
            port=cnavconstants.publishers.INERTIAL_SENSORS_PORT
        )
        self.compass_subscriber = pubsub.LastMessageSubscriber(
            publishers=(inertial_service, ),
            topics=(cnavconstants.topics.COMPASS, ),
        )
        self.orientation_subscriber = pubsub.LastMessageSubscriber(
            publishers=(inertial_service, ),
            topics=(cnavconstants.topics.ORIENTATION, ),
        )

        environmental_service = self.get_sense_service_address(
            port=cnavconstants.publishers.ENVIRONMENTAL_SENSORS_PORT
        )
        self.temperature_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.TEMPERATURE, ),
        )
        self.pressure_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.PRESSURE, ),
        )
        self.humidity_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.HUMIDITY, ),
        )

        self.joystick_subscriber = pubsub.Subscriber(
            publishers=(self.get_sense_service_address(
                port=cnavconstants.publishers.JOYSTICK_PORT
            ), ),
            topics=(cnavconstants.topics.JOYSTICK, ),
        )
        # Do not wait for joystick input - timeout after 1 ms
        self.set_joystick_timeout(timeout=1)

        self.led_matrix_client = clientserver.Client(
            servers=(self.get_sense_service_address(
                port=cnavconstants.servers.LED_MATRIX_PORT
            ), ),
        )

    def cleanup(self):
        logger.info('Cleaning up')
        self.driver.cleanup()

    @property
    def compass(self):
        return self.compass_subscriber.receive().data

    @property
    def orientation(self):
        return self.orientation_subscriber.receive().data

    @property
    def yaw(self):
        return self.orientation['yaw']

    @property
    def temperature(self):
        return self.temperature_subscriber.receive().data

    @property
    def pressure(self):
        return self.pressure_subscriber.receive().data

    @property
    def humidity(self):
        return self.humidity_subscriber.receive().data

    def set_joystick_timeout(self, timeout):
        self.joystick_subscriber.socket.RCVTIMEO = timeout

    @property
    def joystick(self):
        try:
            return self.joystick_subscriber.receive().data
        except zmq.error.Again:
            # this error is raised on timeout - we're only interested in
            # already provided input, thus ignoring
            return None

    @property
    def joystick_direction(self):
        return self.joystick['direction'] if self.joystick else None

    def wait_for_joystick_direction(self):
        logger.info('Waiting for direction from the joystick...')

        while True:
            self.led_matrix_client.request(message=messages.JSON(
                data={
                    'method': 'show_message',
                    'params': {'text': 'Set direction with joystick'}
                }
            ))
            joystick_direction = self.joystick_direction
            if joystick_direction:
                return joystick_direction
            else:
                time.sleep(1)

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
            self.led_matrix_client.request(message=messages.JSON(
                data={
                    'method': 'show_message',
                    'params': {'text': 'Press switch to start'}
                }
            ))
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
        self.motors.forward(steps=self.steps)

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

    def find_free_space(self):
        logger.debug('Finding free space...')
        while not (self.distance >= settings.BOT_DEFAULT_MAX_DISTANCE):
            self.wander()

        self.motors.forward(steps=10)
        logger.debug('Free space found')

    def turn_to_direction(
            self,
            direction,
            tolerance=settings.BOT_DIRECTION_TOLERANCE):

        direction_upper = direction - tolerance
        direction_lower = direction + tolerance

        while direction_lower <= direction <= direction_upper:
            if self.yaw > direction:
                self.motors.left(steps=2)
            else:
                self.motors.right(steps=2)

    def drive_in_direction(self, direction):
        self.find_free_space()
        self.turn_to_direction(direction=direction)
        self.wander()

    def drive_in_direction_continuously(self, direction):
        logger.info('Driving in direction: {}...'.format(
            direction
        ))

        initial_yaw = self.yaw

        while True:
            joystick_direction = self.joystick_direction
            if joystick_direction:
                initial_yaw = self.yaw
                direction = joystick_direction

                logger.info('Driving in direction: {}...'.format(
                    direction
                ))

            desired_yaw = initial_yaw + self.directions.get(direction, 0)
            self.drive_in_direction(direction=desired_yaw)


class Service(services.PublisherService):
    name = 'bot'
    resource = Bot
    address = cnavconstants.publishers.LOCAL_BOT_ADDRESS
    port = cnavconstants.publishers.BOT_SERVICE_PORT


def start():
    return Service().start()


if __name__ == '__main__':
    start()

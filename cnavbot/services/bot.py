import logging
import time

from zmqservices import services
import cnavconstants.topics
import cnavconstants.publishers
import cnavconstants.servers

from cnavbot import settings
from cnavbot.services import bluetooth, camera, pi2go, sense
from cnavbot.utils import log_exceptions

cv2 = settings.CV2
numpy = settings.NUMPY

logger = logging.getLogger()


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
            self.sense = sense.Client()

    def run(self):
        with log_exceptions():
            if settings.BOT_WAIT_FOR_BUTTON_PRESS:
                self.wait_till_switch_pressed()

            if settings.BOT_IN_FOLLOW_DIRECTION_MODE:
                self.drive_in_direction_continuously(
                    direction=self.wait_for_joystick_direction()
                )

            elif settings.BOT_IN_FOLLOW_DIRECTION_AND_LINE_MODE:
                self.drive_in_direction_following_line_continuously(
                    direction=self.wait_for_joystick_direction()
                )

            elif settings.BOT_IN_FOLLOW_CAMERA_TARGET_MODE:
                self.drive_to_camera_target_continuously()

            elif settings.BOT_IN_WANDER_MODE:
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
    def yaw(self):
        return self.sense.yaw

    def wait_for_joystick_direction(self):
        logger.info('Waiting for direction from the joystick...')

        while True:
            self.sense.display_text('Set direction with joystick')
            joystick_direction = self.sense.joystick_direction
            if joystick_direction:
                return joystick_direction
            else:
                time.sleep(1)

    @property
    def bluetooth_scan_results(self):
        return self.bluetooth.receive().data

    @property
    def camera_image(self):
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
            self.sense.display_text('Press switch to start')
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

    def turn_to_direction(
            self,
            direction,
            tolerance=settings.BOT_DIRECTION_TOLERANCE):

        direction_upper = direction + tolerance
        direction_lower = direction - tolerance

        while not (direction_lower <= self.yaw <= direction_upper):
            if self.yaw > direction:
                self.motors.left(steps=0.5)
            else:
                self.motors.right(steps=0.5)

    def drive_in_direction(self, direction, initial_direction=None):
        initial_direction = initial_direction or self.yaw
        joystick_direction = self.sense.joystick_direction
        if joystick_direction:
            initial_yaw = self.yaw
            direction = joystick_direction

            logger.info('Driving in direction: {}...'.format(
                direction
            ))

        desired_yaw = initial_yaw + self.directions.get(direction, 0)
        self.turn_to_direction(direction=desired_yaw)
        self.wander()

    def drive_in_direction_continuously(self, direction):
        logger.info('Driving in direction: {}...'.format(
            direction
        ))

        while True:
            self.drive_in_direction(direction=direction)

    def drive_in_direction_following_line_continuously(self, direction):
        logger.info('Driving in direction following line: {}...'.format(
            direction
        ))

        while True:
            self.drive_in_direction(direction=direction)
            self.follow_line()

    def find_target_in_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.medianBlur(image, 5)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        red = cv2.inRange(
            image,
            numpy.array(settings.TARGET_COLOUR_LOW),
            numpy.array(settings.TARGET_COLOUR_HIGH)
        )

        # Find the contours
        contours, hierarchy = cv2.findContours(
            red, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        # Go through each contour
        found_area = -1
        found_x = -1

        for contour in contours:
            x, _, width, height = cv2.boundingRect(contour)
            cx = x + (width / 2)
            area = width * height

            if found_area < area:
                found_area = area
                found_x = cx

        if found_area > 0:
            target = {
                'x': found_x, 'area': found_area
            }
        else:
            target = None

        return target

    def turn_to_camera_target(self, target_x):
        image_center_x = settings.CAMERA_RESOLUTION_X / 2.0
        direction = (target_x - image_center_x) / image_center_x
        if direction > 0:
            self.motors.right(steps=0.5)
        else:
            self.motors.left(steps=0.5)

    def drive_to_camera_target(self, target):
        if target:
            if target['area'] < settings.TARGET_MINIMUM_AREA:
                logger.info('Target area too small')
            else:
                self.turn_to_camera_target(target['x'])
                self.wander()
        else:
            logger.info('No targets found')

    def drive_to_camera_target_continuously(self):
        logger.info('Driving to camera target...')

        while True:
            self.drive_to_camera_target(
                target=self.find_target_in_image(image_path=self.camera_image)
            )


class Service(services.PublisherService):
    name = 'bot'
    resource = Bot
    address = cnavconstants.publishers.LOCAL_BOT_ADDRESS
    port = cnavconstants.publishers.BOT_SERVICE_PORT


def start():
    return Service().start()


if __name__ == '__main__':
    start()

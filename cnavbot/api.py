from collections import deque
from multiprocessing import Process
import subprocess
import time

from cnavbot import settings, logger


class Driver(object):

    def __init__(self, driver=None, *args, **kwargs):
        self.driver = driver or settings.BOT_DRIVER


class Motors(Driver):

    def __init__(self, speed=None, *args, **kwargs):
        super(Motors, self).__init__(*args, **kwargs)
        self.speed = speed or settings.BOT_DEFAULT_SPEED
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
        logger.info('Going forward')
        self.driver.forward(self.speed)

        if steps:
            self.keep_running(steps)

    def reverse(self, steps=None):
        """Sets both motors to reverse"""
        logger.info('Reversing')
        self.driver.reverse(self.speed)

        if steps:
            self.keep_running(steps)

    def left(self, steps=None):
        """Sets motors to turn opposite directions for left spin"""
        logger.info('Spinning left')
        self.driver.spinLeft(self.speed)

        if steps:
            self.keep_running(steps)

    def right(self, steps=None):
        """Sets motors to turn opposite directions for right spin"""
        logger.info('Spinning right')
        self.driver.spinRight(self.speed)

        if steps:
            self.keep_running(steps)

    def keep_running(self, steps):
        logger.info('Keeping running for {} steps'.format(steps))
        time.sleep(0.1 * steps)
        self.stop()

    def stop(self):
        logger.info('Stopping')
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
        logger.info('Setting LED {} to red: {}, green: {}. blue: {}'.format(
            led_number, red, green, blue
        ))
        self.driver.setLED(led_number, red, green, blue)

    def set_all_leds_rbg(self, red, blue, green):
        """Spins right specified number of steps"""
        for led_number in self.led_numbers:
            self.driver.setLED(led_number, red, green, blue)


class ObstacleSensor(Driver):

    def __init__(self, max_distance=None, *args, **kwargs):
        super(ObstacleSensor, self).__init__(*args, **kwargs)
        self.max_distance = max_distance or settings.BOT_DEFAULT_MAX_DISTANCE
        logger.info('Max distance set to {}'.format(self.max_distance))

    def left(self):
        """Returns true if there is an obstacle to the left"""
        obstacle = self.driver.irLeft()
        logger.info('Left obstacle: {}'.format(obstacle))
        return obstacle

    def right(self):
        """Returns true if there is an obstacle to the right"""
        obstacle = self.driver.irRight()
        logger.info('Right obstacle: {}'.format(obstacle))
        return obstacle

    def front(self):
        """Returns true if there is an obstacle in front"""
        obstacle = self.driver.irCentre()
        logger.info('Front obstacle: {}'.format(obstacle))
        return obstacle

    def front_close(self):
        front_close = self.distance() <= self.max_distance
        logger.info('Front obstacle close: {}'.format(front_close))
        return front_close

    def distance(self):
        """
        Returns the distance in cm to the nearest reflecting object
        in front of the bot
        """
        distance = self.driver.getDistance()
        logger.info('Distance: {}'.format(distance))
        return distance

    def any(self):
        """Returns true if there is any obstacle"""
        any_obstacle = self.driver.irAll()
        logger.info('Any obstacle: {}'.format(any_obstacle))
        return any_obstacle


class LineSensor(Driver):

    def left(self):
        """Returns the state of the left line sensor"""
        left = self.driver.irLeftLine()
        logger.info('Left line: {}'.format(left))
        return left

    def right(self):
        """Returns the state of the right line sensor"""
        right = self.driver.irRightLine()
        logger.info('Right line: {}'.format(right))
        return right


class Bluetooth(object):

    DEVICE_SETUP_SUCCESS_MSG = "Device setup complete"

    def __init__(self, driver=None, scanner=None, *args, **kwargs):
        self.results = deque()
        self.driver = driver or settings.BLUETOOTH_DRIVER
        self.scanner = scanner or settings.IBEACON_SCANNER
        self.start_scanning()

    def start_scanning(self):
        scanning = Process(
            target=self.scan_continuously,
            args=(self.results, )
        )
        scanning.start()

    @staticmethod
    def load_device_init_script():
        return subprocess.Popen(
            ["bash", settings.BLUETOOTH_INIT_SCRIPT],
            stdout=subprocess.PIPE,
            shell=True
        ).communicate()

    def device_initialised_sucessfully(self, output, error):
        # Checking output as exit code cannot be trusted in this case
        return (self.DEVICE_SETUP_SUCCESS_MSG in output) and not error

    def init_device(self):
        """Initialise bluetooth device"""
        output, error = self.load_device_init_script()
        if not self.device_initialised_sucessfully(output, error):
            # Very often it succeeds immediately on second try
            self.load_device_init_script()

    def scan_continuously(self, results):
        """Scan for nearby bluetooth devices"""
        self.init_device()
        try:
            socket = self.driver.hci_open_dev(0)
            self.scanner.hci_le_set_scan_parameters(socket)
            self.scanner.hci_enable_le_scan(socket)
        except:
            logger.exception("Failed to scan with Bluetooth")
        else:
            while True:
                time.sleep(settings.BLUETOOTH_SCAN_INTERVAL)
                events = self.scanner.parse_events(socket, loop_count=5)
                self.results.clear()
                self.results.append(events)

    @property
    def scan_results(self):
        return self.results.pop()


class Bot(Driver):
    # Number of steps required for 360 spin
    full_spin_steps = 44
    # Default number of steps
    steps = 3

    def __init__(
            self, name=None, speed=None, max_distance=None, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.driver.init()
        self.name = name or settings.BOT_DEFAULT_NAME
        logger.info('Bot name set to: {}'.format(self.name))
        self.motors = Motors(speed=speed, driver=self.driver)
        self.lights = Lights(driver=self.driver)
        self.line_sensor = LineSensor(driver=self.driver)
        self.obstacle_sensor = ObstacleSensor(
            max_distance=max_distance, driver=self.driver
        )
        self.bluetooth = Bluetooth()

    def cleanup(self):
        logger.info('Cleaning up')
        self.driver.cleanup()

    @property
    def left_line(self):
        return self.line_sensor.left()

    @property
    def right_line(self):
        return self.line_sensor.right()

    @property
    def switch_pressed(self):
        switch_pressed = self.driver.getSwitch()
        logger.info('Switch pressed: {}'.format(switch_pressed))
        return switch_pressed

    def wait_till_switch_pressed(self):
        while True:
            logger.info('Waiting for switch to be pressed')
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
            logger.info('Avoiding left obstacle')
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid left obstacle')
                return
            self.motors.right(steps=self.steps)
            step_counter += self.steps

    def avoid_right_obstacle(self):
        step_counter = 0
        while self.right_obstacle:
            logger.info('Avoiding right obstacle')
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid right obstacle')
                return
            self.motors.left(steps=self.steps)
            step_counter += self.steps

    def avoid_front_obstacle(self):
        while self.front_obstacle:
            logger.info('Avoiding front obstacle')
            if not self.right_obstacle:
                self.motors.right(steps=self.steps)
            elif not self.left_obstacle:
                self.motors.left(steps=self.steps)
            else:
                while self.front_obstacle_close:
                    self.motors.reverse(steps=self.steps)

    def avoid_obstacles(self):
        while self.any_obstacle:
            logger.info('Avoiding obstacles')
            self.avoid_front_obstacle()
            self.avoid_left_obstacle()
            self.avoid_right_obstacle()

    def wander(self):
        logger.info('Wandering')
        self.avoid_obstacles()
        self.motors.forward()
        self.motors.keep_running(steps=self.steps)

    def wander_continuously(self):
        while True:
            self.wander()

    def follow_line(self):
        last_left = False
        last_right = False
        if self.left_line and self.right_line:
            self.motors.forward()
        elif self.left_line:
            last_left = True
            last_right = False
            self.motors.left(steps=1)
        elif self.right_line:
            last_right = True
            last_left = False
            self.motors.right(steps=1)
        elif not self.left_line and not self.right_line:
            self.reverse(steps=2)
            if last_right:
                self.motors.right(steps=2)
            if last_left:
                self.motors.left(steps=2)

    def follow_line_continuously(self):
        while True:
            self.follow_line()

    def follow_line_and_avoid_obstacles(self):
        self.avoid_obstacles()
        self.follow_line()

    def follow_line_and_avoid_obstacles_continuously(self):
        while True:
            self.follow_line_and_avoid_obstacles()

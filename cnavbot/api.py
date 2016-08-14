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
        self.driver.forward(self.speed)

        if steps:
            self.keep_running(steps)

    def reverse(self, steps=None):
        """Sets both motors to reverse"""
        self.driver.reverse(self.speed)

        if steps:
            self.keep_running(steps)

    def left(self, steps=None):
        """Sets motors to turn opposite directions for left spin"""
        self.driver.spinLeft(self.speed)

        if steps:
            self.keep_running(steps)

    def right(self, steps=None):
        """Sets motors to turn opposite directions for right spin"""
        self.driver.spinRight(self.speed)

        if steps:
            self.keep_running(steps)

    def keep_running(self, steps):
        time.sleep(0.1 * steps)
        self.stop()

    def stop(self):
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
        self.driver.setLED(led_number, red, green, blue)

    def set_all_leds_rbg(self, red, blue, green):
        """Spins right specified number of steps"""
        for led_number in self.led_numbers:
            self.driver.setLED(led_number, red, green, blue)


class ObstacleSensor(Driver):

    def __init__(self, max_distance=None, *args, **kwargs):
        super(ObstacleSensor, self).__init__(*args, **kwargs)
        self.max_distance = max_distance or settings.BOT_DEFAULT_MAX_DISTANCE

    def left(self):
        """Returns true if there is an obstacle to the left"""
        return self.driver.irLeft()

    def right(self):
        """Returns true if there is an obstacle to the right"""
        return self.driver.irRight()

    def front(self):
        """Returns true if there is an obstacle in front"""
        return self.driver.irCentre()

    def distance(self):
        """
        Returns the distance in cm to the nearest reflecting object
        in front of the bot
        """
        return self.driver.getDistance()

    def any(self):
        """Returns true if there is any obstacle"""
        return self.driver.irAll()


class LineSensor(Driver):

    def left(self):
        """Returns the state of the left line sensor"""
        return self.driver.irLeftLine()

    def right(self):
        """Returns the state of the right line sensor"""
        return self.driver.irRightLine()


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
        self.motors = Motors(speed=speed, driver=self.driver)
        self.lights = Lights(driver=self.driver)
        self.line_sensor = LineSensor(driver=self.driver)
        self.obstacle_sensor = ObstacleSensor(
            max_distance=max_distance, driver=self.driver
        )

    def cleanup(self):
        self.driver.cleanup()

    @property
    def switch_pressed(self):
        return self.driver.getSwitch()

    def wait_till_switch_pressed(self):
        while True:
            if self.switch_pressed:
                return
            else:
                time.sleep(1)

    @property
    def front_obstacle(self):
        return self.obstacle_sensor.front()

    @property
    def left_obstacle(self):
        return self.obstacle_sensor.left()

    @property
    def right_obstacle(self):
        return self.obstacle_sensor.right()

    @property
    def any_obstacle(self):
        return any(
            (self.front_obstacle, self.left_obstacle, self.right_obstacle)
        )

    @property
    def distance(self):
        return self.obstacle_sensor.distance()

    def avoid_left_obstacle(self):
        step_counter = 0
        while self.left_obstacle:
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid left obstacle')
                return
            self.motors.right(steps=self.steps)
            step_counter += self.steps

    def avoid_right_obstacle(self):
        step_counter = 0
        while self.right_obstacle:
            if step_counter >= self.full_spin_steps:
                logger.warning('Failed to avoid right obstacle')
                return
            self.motors.left(steps=self.steps)
            step_counter += self.steps

    def avoid_front_obstacle(self):
        while self.front_obstacle:
            if not self.right_obstacle:
                self.motors.right(steps=self.steps)
            elif not self.left_obstacle:
                self.motors.left(steps=self.steps)
            else:
                self.motors.reverse(steps=self.steps)

    def avoid_obstacles(self):
        while self.any_obstacle:
            self.avoid_front_obstacle()
            self.avoid_left_obstacle()
            self.avoid_right_obstacle()

    def wander(self):
        while True:
            self.avoid_obstacles()
            self.motors.forward()
            self.motors.keep_running(steps=self.steps)

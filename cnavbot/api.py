from cnavbot import settings


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

    def forward(self):
        """Sets both motors to go forward"""
        self.driver.forward(self.speed)

    def reverse(self):
        """Sets both motors to reverse"""
        self.driver.reverse(self.speed)

    def spin_left(self):
        """Sets motors to turn opposite directions for left spin"""
        self.driver.spinLeft(self.speed)

    def spin_right(self):
        """Sets motors to turn opposite directions for right spin"""
        self.driver.spinRight(self.speed)

    def step_forward(self, steps):
        """Moves forward specified number of steps"""
        self.driver.stepForward(self.speed, steps)

    def step_reverse(self, steps):
        """Moves backward specified number of steps"""
        self.driver.stepReverse(self.speed, steps)

    def step_spin_left(self, steps):
        """Spins left specified number of steps"""
        self.driver.stepSpinL(self.speed, steps)

    def step_spin_right(self, steps):
        """Spins right specified number of steps"""
        self.driver.stepSpinR(self.speed, steps)

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

    def __init__(self, name=None, speed=None, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.driver.init()
        self.name = name or settings.BOT_DEFAULT_NAME
        self.motors = Motors(speed=speed, driver=self.driver)
        self.lights = Lights(driver=self.driver)
        self.obstacle_sensor = ObstacleSensor(driver=self.driver)
        self.line_sensor = LineSensor(driver=self.driver)

    def cleanup(self):
        self.driver.cleanup()

    @property
    def left_obstacle(self):
        return self.obstacle_sensor.left()

    @property
    def right_obstacle(self):
        return self.obstacle_sensor.right()

    @property
    def distance(self):
        return self.obstacle_sensor.distance()

    def avoid_left_obstacle(self):
        while self.left_obstacle:
            self.motors.spin_right()
            self.motors.stop()

    def avoid_right_obstacle(self):
        while self.right_obstacle:
            self.motors.spin_left()
            self.motors.stop()

    def avoid_front_obstacle(self):
        while self.distance <= 0.2:
            self.motors.spin_right()
            self.motors.stop()

    def wander(self):
        while True:
            self.avoid_left_obstacle()
            self.avoid_right_obstacle()
            while not (self.left_obstacle or self.right_obstacle):
                self.avoid_front_obstacle()
                self.motors.forward()
            self.motors.stop()

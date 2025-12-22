import wiringpi
import time
from wiringpi import GPIO

class StepperDriver:
    def __init__(self, dir, stp, slp, rst, ms3, ms2, ms1, en):
        """Initialize the stepper with the provided pins
        Args:
            dir (int): Direction Pin
            stp (int): Step Pin
            slp (int): Sleep Pin
            rst (int): Reset Pin
            ms3 (int): Microstep Select 3 Pin
            ms2 (int): Microstep Select 2 Pin
            ms1 (int): Microstep Select 1 Pin
            en (int): Enable Pin
        """

        #Set Pin Numbers
        self.dir = dir
        self.stp = stp
        self.slp = slp
        self.rst = rst
        self.ms3 = ms3
        self.ms2 = ms2
        self.ms1 = ms1
        self.en  = en

        #Configure Pins
        wiringpi.pinMode(self.dir, GPIO.OUTPUT)
        wiringpi.pinMode(self.stp, GPIO.OUTPUT)
        wiringpi.pinMode(self.slp, GPIO.OUTPUT)
        wiringpi.pinMode(self.rst, GPIO.OUTPUT)
        wiringpi.pinMode(self.ms3, GPIO.OUTPUT)
        wiringpi.pinMode(self.ms2, GPIO.OUTPUT)
        wiringpi.pinMode(self.ms1, GPIO.OUTPUT)
        wiringpi.pinMode(self.en, GPIO.OUTPUT)

        #Initialization Functions
        self.sleep_mode(sleepy = False)
        self.enable_stepper(enabled = False)
        self.set_microstep(step_size=1)
        self.set_direction(0)

        #Initialize Remaining Pins
        wiringpi.digitalWrite(self.rst, GPIO.HIGH)
        wiringpi.digitalWrite(self.stp, GPIO.LOW)

        self.DEGREES_PER_STEP = 1.8
        self.speed = 1      #Degreees per second

    @property
    def speed(self):
        return(self.speed)
    
    
    def set_microstep(self, step_size):
        """Set mirco-stepping level

        Args:
            step_size (int): Can be 1 (none), 2 (half),  4 (quarter), 8 (eigth), 16 (sixteenth)
        """

        self.step_size = step_size
        
        if (self.step_size == 1):
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
        
        elif (self.step_size == 2):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (self.step_size == 4):
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (self.step_size == 8):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (self.step_size == 16):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)

        else:
            #Default to no micro-stepping
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

    def sleep_mode(self, sleepy):
        """Tucks stepper in for a nap

        Args:
            sleepy (bool): If true, sleeps the driver, if false, wakes up driver
        """
        self.sleepy = sleepy

        if sleepy:
            wiringpi.digitalWrite(self.slp, GPIO.LOW)
        else:
            wiringpi.digitalWrite(self.slp, GPIO.HIGH)
            time.sleep(1/1000.0)  #Wait for driver to wake up

    def enable_stepper(self, enabled):
        """Enables or disables the stepper.

        Args:
            enabled (bool): Enable stepper if True, disable stepper if False
        """
        self.enabled = enabled

        if enabled:
            wiringpi.digitalWrite(self.en, GPIO.HIGH)
        else:
            wiringpi.digitalWrite(self.en, GPIO.LOW)

    def set_direction(self, direction):
        """Set the direction of the stepper

        Args:
            direction (int): 0 or 1, direction depends on application
        """
        self.direction = direction

        if self.direction == 0:
            wiringpi.digitalWrite(self.dir, GPIO.LOW)
        elif self.direction == 1:
            wiringpi.digitalWrite(self.dir, GPIO.HIGH)

    def step(self):
        """Performs one step, waiting minimum time between, likely not accurate timing
        """
        wiringpi.digitalWrite(self.stp, GPIO.HIGH)
        time.sleep(1/1000000.0)
        wiringpi.digitalWrite(self.stp, GPIO.LOW)
        time.sleep(1/1000000.0)

    def set_speed(self, speed):
        self.speed = speed

    def rotate_degrees(self, angle, direction):
        """Rotates a stepper by a certain angle

        Args:
            angle (float): Angle to rotate in degrees
            direction (int): 0 or 1, direction depends on application
        """
        self.set_direction(direction)
        steps = angle/(self.DEGREES_PER_STEP*self.step_size)
        delay_time = (steps*self.DEGREES_PER_STEP*self.step_size)/self.speed

        for i in range(steps):
            time.sleep(delay_time)
            self.step()

    def rotate_degrees_by_time(self, angle, direction, secs):
        """Rotate a stepper by a number of degrees over a given time

        Args:
            angle (float): Angle to rotate in degrees
            direction (int): 0 or 1, direction depends on application
            secs (_type_): _description_
        """

        self.set_direction(direction)
        steps = angle/(self.DEGREES_PER_STEP*self.step_size)
        delay_time = secs/steps
        for i in range(steps):
            time.sleep(delay_time)
            self.step()






    
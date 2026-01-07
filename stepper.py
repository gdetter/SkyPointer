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
        wiringpi.wiringPiSetup()
        
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

        #Initialize Remaining Pins
        wiringpi.digitalWrite(self.rst, GPIO.HIGH)
        wiringpi.digitalWrite(self.stp, GPIO.LOW)

        #Initialize Properties
        self.DEGREES_PER_STEP = 1.8
        self._reversed = False
        self._sleeping = False
        self._microstep = 1     #No microstepping
        self._speed = 100       #Degreees per second
        self._ratio = 1         #Mechanical ratio (_ratio:1)   
        self._enabled = False   #Disable the stepper

    @property
    def speed(self):
        """Get and set the speed of the stepper. Speed is in degrees per second.
        """
        return(self._speed)

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def ratio(self):
        """Get and set the ratio of the stepper. This effectively changes the steps per rotation.
        """
        return(self._advantage)
    
    @ratio.setter
    def ratio(self, value):
        self._ratio = value

    @property
    def microstep(self):
        """Get and set the microstepping level.

        Returns:
            int: Can be 1 (none), 2 (half),  4 (quarter), 8 (eigth), 16 (sixteenth)
        """
        return self._microstep
    
    @microstep.setter
    def microstep(self, value):
        self._microstep = value
        if (value == 1):
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
        
        elif (value == 2):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (value == 4):
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (value == 8):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

        elif (value == 16):
            wiringpi.digitalWrite(self.ms1, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)
            wiringpi.digitalWrite(self.ms2, GPIO.HIGH)

        else:
            #Default to no micro-stepping
            self._microstep = 1
            wiringpi.digitalWrite(self.ms1, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)
            wiringpi.digitalWrite(self.ms2, GPIO.LOW)

    @property
    def enabled(self):
        """Set to True to enable and False to disable.

        Returns:
            bool: True if enabled, false if disabled
        """
        return self._enabled()
    
    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._enabled:
            wiringpi.digitalWrite(self.en, GPIO.LOW)
        else:
            wiringpi.digitalWrite(self.en, GPIO.HIGH)

    
    @property
    def sleeping(self):
        """Tucks stepper in for a nap if true, wakes up if false.

        Returns:
            bool: True if sleeping, False if awake
        """
        return self._sleeping
    
    @sleeping.setter
    def sleeping(self, value):
        self._sleeping = value
        if self._sleeping:
            wiringpi.digitalWrite(self.slp, GPIO.LOW)
        else:
            wiringpi.digitalWrite(self.slp, GPIO.HIGH)
            time.sleep(1/1000.0)  #Wait for driver to wake up

    @property
    def reversed(self):
        """Reversed direction of stepper if set to True

        Returns:
            bool: True if reversed, false if not
        """
        return self._reversed
    
    @reversed.setter
    def reversed(self, value):
        self._reversed = value
        if not self._reversed:
            wiringpi.digitalWrite(self.dir, GPIO.LOW)
        else:
            wiringpi.digitalWrite(self.dir, GPIO.HIGH)
   
    def step(self):
        """Performs one step, waiting minimum time between, likely not accurate timing
        """
        wiringpi.digitalWrite(self.stp, GPIO.HIGH)
        time.sleep(1/1000000.0)
        wiringpi.digitalWrite(self.stp, GPIO.LOW)
        time.sleep(1/1000000.0)

    def rotate_degrees(self, angle):
        """Rotates a stepper by a certain angle

        Args:
            angle (float): Angle to rotate in degrees
        """
        steps = angle*self._ratio*self._microstep/self.DEGREES_PER_STEP
        delay_time = self.DEGREES_PER_STEP*self._microstep/self._speed/self._ratio

        #Toggle direction if needed
        if angle < 0:
            self._reversed = not self._reversed

        #Perform the motion
        for i in range(int(steps)):
            time.sleep(delay_time)
            self.step()

        #Toggle direction back if needed
        if angle < 0:
            self._reversed = not self._reversed

    def rotate_degrees_by_time(self, angle, secs):
        """Rotate a stepper by a number of degrees over a given time

        Args:
            angle (float): Angle to rotate in degrees
            secs (float): Time to perform rotation over
        """
        #Toggle direction if needed
        if angle < 0:
            self._reversed = not self._reversed

        #Perform the motion
        steps = angle*self._ratio*self._microstep/self.DEGREES_PER_STEP
        delay_time = secs/steps
        for i in range(steps):
            time.sleep(delay_time)
            self.step()

        #Toggle direction back if needed
        if angle < 0:
            self._reversed = not self._reversed






    

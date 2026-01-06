from stepper import StepperDriver
import time

PIN19 = 11
PIN21 = 12
PIN23 = 14
PIN27 = 17
PIN29 = 19
PIN31 = 20
PIN33 = 22
PIN35 = 23
PIN37 = 25

PIN22 = 13
PIN24 = 15
PIN26 = 16
PIN28 = 18
PIN32 = 21
PIN36 = 24
PIN38 = 26
PIN40 = 27


motor1 = StepperDriver(dir=PIN27, stp=PIN29, slp = PIN31, rst = PIN33, ms3 = PIN19, ms2 = PIN21, ms1 = PIN23, en = PIN35)
motor2 = StepperDriver(dir=PIN22, stp=PIN24, slp=PIN26, rst=PIN28, ms3=PIN36, ms2=PIN38, ms1=PIN40, en=PIN32)
motor1.enable_stepper(enabled = True)
motor2.enable_stepper(enabled = True)
motor1.set_direction(1)
motor2.set_direction(1)
motor1.set_microstep(16)
motor2.set_microstep(16)
while True:
    motor1.rotate_degrees(360, 0)
    motor2.rotate_degrees(360, 0)
    time.sleep(1)
    motor1.rotate_degrees(360, 1)
    motor2.rotate_degrees(360, 1)
    time.sleep(1)

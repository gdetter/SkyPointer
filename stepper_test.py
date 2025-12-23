from stepper import StepperDriver
import time

PIN21 = 12
PIN23 = 14
PIN27 = 17
PIN29 = 19
PIN31 = 20
PIN33 = 22
PIN35 = 23
PIN37 = 25


motor1 = StepperDriver(dir=PIN21, stp=PIN23, slp = PIN27, rst = PIN29, ms3 = PIN31, ms2 = PIN33, ms1 = PIN35, en = PIN37)

while True:
    motor1.set_speed(10)
    motor1.set_direction(0)
    motor1.rotate_degrees(360)
    time.sleep(1)
    motor1.set_direction(1)
    motor1.rotate_degrees_by_time(360,15)
    time.sleep(1)
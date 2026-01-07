from stepper import StepperDriver
import time
import threading

# Pin Definitions
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


#Connect to Steppers
motor1 = StepperDriver(dir=PIN27, stp=PIN29, slp = PIN31, rst = PIN33, ms3 = PIN19, ms2 = PIN21, ms1 = PIN23, en = PIN35)
# motor2 = StepperDriver(dir=PIN22, stp=PIN24, slp=PIN26, rst=PIN28, ms3=PIN36, ms2=PIN38, ms1=PIN40, en=PIN32)

#Configure Steppers
motor1.ratio = 12
motor1.microstep = 16
motor1.speed = 50
# motor2.ratio = 3.6
# motor2.microstep = 16

#Enable Steppers
motor1.enabled = True
print(motor1.enabled)
# motor2.enabled = True

while True:
    print("A")
    motor1.rotate_degrees(360)
    print("B")
    time.sleep(1)
    print("C")
    motor1.rotate_degrees(-360)
    print("D")
    time.sleep(1)
    print("E")
    # t1 = threading.Thread(target=motor1.rotate_degrees, kwargs={'angle':360})
    # t2 = threading.Thread(target=motor2.rotate_degrees, kwargs={'angle':360})
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    # time.sleep(1)
    # t1 = threading.Thread(target=motor1.rotate_degrees, kwargs={'angle':-360})
    # t2 = threading.Thread(target=motor2.rotate_degrees, kwargs={'angle':-360})
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    # time.sleep(1)

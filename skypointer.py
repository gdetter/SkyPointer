import os
import geocoder
import urllib.request
from skyfield.api import N, S, E, W, wgs84, EarthSatellite, load
import csv
import time
from stepper import StepperDriver
import time
import threading
from enum import Enum, auto
import wiringpi
from wiringpi import GPIO
import concurrent.futures

class state(Enum):
    INITIALIZING = auto()
    DISABLED = auto()
    STARTING = auto()
    TRACKING = auto()
    STOPPING = auto()
    POWERING_DOWN = auto()

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
PIN18 = 10
BUTTON_PIN = PIN18

#Connect to Steppers
alt_motor = StepperDriver(dir=PIN27, stp=PIN29, slp = PIN31, rst = PIN33, ms3 = PIN19, ms2 = PIN21, ms1 = PIN23, en = PIN35)
az_motor = StepperDriver(dir=PIN22, stp=PIN24, slp=PIN26, rst=PIN28, ms3=PIN36, ms2=PIN38, ms1=PIN40, en=PIN32)

#Configure Steppers
alt_motor.ratio = 12
alt_motor.microstep = 16
alt_motor.speed = 20
alt_motor.reversed = True
az_motor.ratio = 3.6
az_motor.microstep = 16
az_motor.speed = 20
az_motor.reversed = True
alt_motor.enabled = False
az_motor.enabled = False

#Initialize Current Angles
current_alt = -90
current_az = 0

ts = None
iss = None
me = None

button_pressed = False
button_start = None


#Initialize State
current_state = state.INITIALIZING

def get_my_ip():
    external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    return(external_ip)

def get_lat_lon():
    g = geocoder.ipinfo(get_my_ip())
    return g.latlng

def download_sats():
    max_days = 7.0         # download again once 7 days old
    name = 'stations.csv'  # custom filename, not 'gp.php'
    base = 'https://celestrak.org/NORAD/elements/gp.php'
    url = base + '?GROUP=stations&FORMAT=csv'
    if not load.exists(name) or load.days_old(name) >= max_days:
        load.download(url, filename=name)

def button_callback():
    global button_pressed
    global button_start
    global current_state

    if  not button_pressed:
        print('Button Pressed')
        button_pressed = True
        time.sleep(0.5)
        button_start = time.perf_counter_ns()
    elif button_start is not None:
        print('Button Released')
        now = time.perf_counter_ns()
        time.sleep(0.5)
        delta = now - button_start
        if delta > 10000000000:
            print('Long Press')
            current_state = state.POWERING_DOWN
        elif delta > 2000000000:
            print('Short Press')
            if current_state == state.DISABLED:
                print('Starting...')
                current_state = state.STARTING
            elif current_state == state.TRACKING:
                print('Stopping...')
                current_state = state.STOPPING
        button_start = None
        button_pressed = False

def power_down():

    alt_motor.enabled = True
    az_motor.enabled = True
    alt_motor.microstep = 1
    az_motor.microstep = 1

    for i in range(750):
        alt_motor.step()
        az_motor.step()
        time.sleep(0.0005)
        alt_motor.reversed = not alt_motor.reversed
        az_motor.reversed = not az_motor.reversed
        if i %250 == 0:
            time.sleep(0.3)
    
    os.system('systemctl poweroff') 

def initialize():
    global iss
    global me
    global current_state
    global ts
    print('Initializing...')

    #Configure Button
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(BUTTON_PIN, wiringpi.GPIO.INPUT)
    wiringpi.pullUpDnControl(BUTTON_PIN, wiringpi.GPIO.PUD_UP)
    wiringpi.wiringPiISR(BUTTON_PIN, wiringpi.GPIO.INT_EDGE_BOTH, button_callback)

    #Get current location
    my_lat, my_lon = get_lat_lon()
    print(f"Lattitude: {my_lat}/nLongitude: {my_lon}")
    me = wgs84.latlon(my_lat * N, my_lon * E)

    #Load ISS
    download_sats()
    ts = load.timescale()
    with load.open('stations.csv', mode='r') as f:
        data = list(csv.DictReader(f))
    sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
    print('Loaded', len(sats), 'satellites')
    by_name = {sat.name: sat for sat in sats}
    iss = by_name['ISS (ZARYA)']
    alt_motor.enabled = True
    az_motor.enabled = True
    alt_motor.microstep = 1
    az_motor.microstep = 1
    for i in range(250):
        alt_motor.step()
        az_motor.step()
        time.sleep(0.0005)
        alt_motor.reversed = not alt_motor.reversed
        az_motor.reversed = not az_motor.reversed
    alt_motor.microstep = 16
    az_motor.microstep = 16
    alt_motor.enabled = False
    az_motor.enabled = False
    print('Waiting...')
    current_state = state.DISABLED

def start_tracking():
    global iss
    global me
    global current_alt
    global current_az
    global current_state

    alt_motor.enabled = True
    az_motor.enabled = True
    t = ts.now()
    difference = iss - me
    topocentric = difference.at(t)
    target_alt, target_az, target_distance = topocentric.altaz()
    print(target_az)
    alt_delta = target_alt.degrees-current_alt
    az_delta = target_az.degrees-current_az
    print(target_az)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        alt_future = executor.submit(alt_motor.rotate_degrees_by_time,alt_delta, 10)
        az_future = executor.submit(az_motor.rotate_degrees_by_time,az_delta, 10)
        alt_degs = alt_future.result()
        az_degs = az_future.result()
    
    current_alt = current_alt+alt_degs
    current_az = current_az+az_degs
    current_state = state.TRACKING

def tracking():
    global iss
    global me
    global current_alt
    global current_az
    t = ts.now()
    difference = iss - me
    topocentric = difference.at(t)
    target_alt, target_az, target_distance = topocentric.altaz()
    alt_delta = target_alt.degrees - current_alt
    az_delta = target_az.degrees - current_az
    with concurrent.futures.ThreadPoolExecutor() as executor:
        alt_future = executor.submit(alt_motor.rotate_degrees,alt_delta)
        az_future = executor.submit(az_motor.rotate_degrees,az_delta)
        alt_degs = alt_future.result()
        az_degs = az_future.result()
    current_alt = current_alt+alt_degs
    current_az = current_az+az_degs
    print(f'Current Altitude: {current_alt}')
    print(f'Current Azimuth: {current_az}')
    time.sleep(0.1)

def stop_tracking():
    global current_alt
    global current_az
    global current_state
    target_alt = -90
    target_az = 0
    alt_delta = target_alt-current_alt
    az_delta = target_az-current_az
    alt_thread = threading.Thread(target=alt_motor.rotate_degrees, kwargs={'angle':alt_delta})
    az_thread = threading.Thread(target=az_motor.rotate_degrees, kwargs={'angle':az_delta})
    alt_thread.start()
    az_thread.start()
    alt_thread.join()
    az_thread.join()
    current_alt = target_alt
    current_az = target_az
    alt_motor.enabled = False
    az_motor.enabled = False
    current_state = state.DISABLED

while True:
    match current_state:
        case state.INITIALIZING:
            initialize()
        case state.DISABLED:
            pass
        case state.STARTING:
            start_tracking()
        case state.STOPPING:
            stop_tracking()
        case state.TRACKING:
            tracking()
        case state.POWERING_DOWN:
            power_down()


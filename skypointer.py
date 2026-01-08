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

class state(Enum):
    INITIALIZING = auto()
    DISABLED = auto()
    STARTING = auto()
    TRACKING = auto()
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
alt_motor.speed = 10
alt_motor.reversed = True
az_motor.ratio = 3.6
az_motor.microstep = 16
az_motor.speed = 10
alt_motor.reversed = True

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
        time.sleep(0.1)
        button_start = time.perf_counter_ns()
    else:
        print('Button Released')
        now = time.perf_counter_ns()
        time.sleep(0.1)
        delta = now - button_start
        if delta > 10000000000:
            print('Long Press')
            current_state = state.POWERING_DOWN
        button_pressed = False

def power_down():
    os.system('systemctl poweroff') 

def initialize():
    global iss
    global me
    global current_state
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
    print('Waiting...')
    current_state = state.DISABLED

while True:
    match current_state:
        case state.INITIALIZING:
            initialize()
        case state.DISABLED:
            alt_motor.enabled = False
            az_motor.enabled = False
            # print('Disabled')
        case state.STARTING:
            pass
        case state.TRACKING:
            pass
        case state.POWERING_DOWN:
            pass





#Enable Steppers
alt_motor.enabled = True
az_motor.enabled = True
while True:
    
    while started:
        t = ts.now()
        difference = iss - me
        topocentric = difference.at(t)
        target_alt, target_az, target_distance = topocentric.altaz()
        # astrometric = me.at(t).observe(mars)
        # target_alt, target_az, d = astrometric.apparent().altaz()
        print(f'Target Altitude: {target_alt.degrees}')
        print(f'Target Azimuth: {target_az.degrees}')
        alt_delta = target_alt.degrees-current_alt
        az_delta = target_az.degrees-current_az

        alt_thread = threading.Thread(target=alt_motor.rotate_degrees, kwargs={'angle':alt_delta})
        az_thread = threading.Thread(target=az_motor.rotate_degrees, kwargs={'angle':az_delta})
        alt_thread.start()
        az_thread.start()
        alt_thread.join()
        az_thread.join()
    
        current_alt = current_alt + alt_delta
        current_az = current_az + az_delta
        time.sleep(1)
    

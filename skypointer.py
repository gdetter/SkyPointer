import geocoder
import urllib.request
from skyfield.api import N, S, E, W, wgs84
from skyfield.api import load
import csv
from skyfield.api import EarthSatellite, load
import time
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
motor2 = StepperDriver(dir=PIN22, stp=PIN24, slp=PIN26, rst=PIN28, ms3=PIN36, ms2=PIN38, ms1=PIN40, en=PIN32)

#Configure Steppers
motor1.ratio = 12
motor1.microstep = 16
motor1.speed = 10
motor2.ratio = 3.6
motor2.microstep = 16
motor1.speed = 10

#Initialize current position
current_alt = -90
current_az = 0

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

#Get current location
my_lat, my_lon = get_lat_lon()

print(f"Lattitude: {my_lat}/nLongitude: {my_lon}")
download_sats()
ts = load.timescale()
t = ts.now()
with load.open('stations.csv', mode='r') as f:
    data = list(csv.DictReader(f))

sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
print('Loaded', len(sats), 'satellites')

# Load the JPL ephemeris DE421 (covers 1900-2050).

print("Loading JPL Ephemeris DE421...")
planets = load('de421.bsp')
earth, mars = planets['earth'], planets['mars']
me = earth + wgs84.latlon(my_lat * N, my_lon * E)
#Enable Steppers
motor1.enabled = True
motor2.enabled = True
while True:
    # What's the position of Mars, viewed from Earth?
    t = ts.now()
    astrometric = me.at(t).observe(mars)
    target_alt, target_az, d = astrometric.apparent().altaz()
    print(f'Target Altitude: {target_alt.degrees}')
    print(f'Target Azimuth: {target_az.degrees}')
    alt_delta = target_alt-current_alt
    motor1.rotate_degrees(angle=alt_delta)
    time.sleep(1)
    

import skyfield
import geocoder
import urllib.request
from skyfield.api import N, S, E, W, wgs84
from skyfield.api import load
import csv
from skyfield.api import EarthSatellite, load


def get_my_ip():
    external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    return(external_ip)

def get_lat_lon():
    g = geocoder.ipinfo(get_my_ip())
    return g.latlng

verbose = True

if(verbose):
    print("Getting Latitude and Longitude...")

my_lat, my_lon = get_lat_lon()


# Load Satellite Data
max_days = 7.0         # download again once 7 days old
name = 'stations.csv'  # custom filename, not 'gp.php'

base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=stations&FORMAT=csv'

if not load.exists(name) or load.days_old(name) >= max_days:
    load.download(url, filename=name)


# Create a timescale and ask the current time.
if(verbose):
    print("Getting Timescale...")
ts = load.timescale()
t = ts.now()

with load.open('stations.csv', mode='r') as f:
    data = list(csv.DictReader(f))

sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
print('Loaded', len(sats), 'satellites')

# Load the JPL ephemeris DE421 (covers 1900-2050).
if(verbose):
    print("Loading JPL Ephemeris DE421...")
planets = load('de421.bsp')
earth, mars = planets['earth'], planets['mars']

# What's the position of Mars, viewed from Earth?
if(verbose):
    print("Calculating...")
astrometric = earth.at(t).observe(mars)
ra, dec, distance = astrometric.radec()

print(f"Right Ascension: {ra}")
print(f"Declination: {dec}")
print(f"Distance: {distance}")

boston = earth + wgs84.latlon(my_lat * N, my_lon * E)
astrometric = boston.at(t).observe(mars)
alt, az, d = astrometric.apparent().altaz()

print(alt)
print(az)
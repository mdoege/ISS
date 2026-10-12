#!/usr/bin/env python

# Plot predicted ISS path with Matplotlib and Cartopy

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.feature.nightshade import Nightshade
import cartopy.feature as cfeature
from skyfield.api import load, wgs84, utc, EarthSatellite
import csv, datetime

hours = 2  # number of hours to plot

cities = open("cities.tsv").readlines()

plt.figure(figsize=(100, 50))
ax = plt.axes((0, 0, 1, 1), projection=ccrs.PlateCarree())
ax.stock_img()
ax.coastlines(resolution="10m")
# ax.add_feature(Nightshade(datetime.datetime.utcnow(), alpha=0.2))
ax.add_feature(cfeature.LAND)
# ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES)

# download new orbital elements each day;
# see code at https://rhodesmill.org/skyfield/earth-satellites.html

csvname = "stations.csv"
base = "https://celestrak.org/NORAD/elements/gp.php"
url = base + "?GROUP=stations&FORMAT=csv"
max_days = 1

if not load.exists(csvname) or load.days_old(csvname) >= max_days:
    load.download(url, filename=csvname)

with load.open(csvname, mode="r") as f:
    data = list(csv.DictReader(f))

ts = load.timescale()
satellites = [EarthSatellite.from_omm(ts, fields) for fields in data]

by_name = {sat.name: sat for sat in satellites}
satellite = by_name["ISS (ZARYA)"]
ts = load.timescale()
tnow = datetime.datetime.now(datetime.timezone.utc)

X, Y = [], []

for x in range(0, 3 * hours * 60):
    td = datetime.timedelta(seconds=20)
    t = tnow + x * td
    t = ts.from_datetime(t)
    geocentric = satellite.at(t)
    lat, lon = wgs84.latlon_of(geocentric)
    iss = lat.degrees, lon.degrees
    X.append(iss[1])
    Y.append(iss[0])
    plt.plot(iss[1], iss[0], "bs", lw=5, transform=ccrs.Geodetic())


for l in cities:
    c = l.split("\t")
    plt.plot(float(c[1]), float(c[0]), "ro", lw=5, transform=ccrs.Geodetic())
    plt.text(
        float(c[1]),
        float(c[0]),
        c[2],
        horizontalalignment="left",
        transform=ccrs.Geodetic(),
    )


# plt.show()
plt.savefig("map2.png")

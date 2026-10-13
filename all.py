#!/usr/bin/env python

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84, utc, EarthSatellite
import csv, time, datetime, os

plt.figure(figsize=(12, 6))
plt.gcf().add_axes((0, 0, 1, 1))  # https://e2eml.school/matplotlib_framing.html#fill

m = Basemap(projection="cyl", resolution="c")

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


while True:
    allxy = []

    for satellite in satellites:
        t = datetime.datetime.now(datetime.timezone.utc)
        t = ts.from_datetime(t)
        geocentric = satellite.at(t)
        lat, lon = wgs84.latlon_of(geocentric)
        y, x = lat.degrees, lon.degrees
        print(x, y, satellite.name)
        show = True
        for xx, yy in allxy:
            d = (x - xx) ** 2 + (y - yy) ** 2
            if d < 0.001:
                show = False
        if show:
            allxy.append((x, y))
            m.plot(x, y, "bs", lw=5)
            plt.text(
                x,
                y,
                satellite.name,
                fontsize=12,
                fontweight="bold",
                ha="left",
                va="bottom",
                color="k",
            )

    m.drawcoastlines()
    m.drawcountries(color="red")
    m.drawstates(color="green")
    # m.drawrivers(color = "blue")
    date = datetime.datetime.now(datetime.timezone.utc)
    m.nightshade(date)
    plt.draw()
    plt.pause(3)
    plt.cla()

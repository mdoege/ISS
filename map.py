#!/usr/bin/env python

# Plot predicted ISS path with Matplotlib and Basemap

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84, utc
import time, datetime, os

hours = 2	# number of hours to plot

cities = open("cities.tsv").readlines()

plt.figure(figsize = (100, 50))
plt.gcf().add_axes((0, 0, 1, 1))  # https://e2eml.school/matplotlib_framing.html#fill

m = Basemap(projection = 'cyl', resolution = 'l')

# from https://rhodesmill.org/skyfield/earth-satellites.html
stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
ts = load.timescale()

def getpos():
	tnow = ts.now()
	geocentric = satellite.at(tnow)
	lat, lon = wgs84.latlon_of(geocentric)
	return lat.degrees, lon.degrees

tnow = datetime.datetime.now(datetime.timezone.utc)

X, Y = [], []

for x in range(0, 3 * hours * 60):
	td = datetime.timedelta(seconds = 20)
	t = tnow + x * td
	t = ts.from_datetime(t)
	geocentric = satellite.at(t)
	lat, lon = wgs84.latlon_of(geocentric)
	iss = lat.degrees, lon.degrees
	X.append(iss[1])
	Y.append(iss[0])

x, y = m(X, Y)
m.plot(x, y, "bs", lw = 5)

for l in cities:
	c = l.split("\t")
	x, y = m(float(c[1]), float(c[0]))
	# https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html#text
	plt.text(x, y, c[2], fontsize = 12, fontweight = 'bold', ha = 'left', va = 'bottom', color = 'k')
	m.scatter(x, y, marker = "o", color = "teal")

m.drawcoastlines()
m.drawcountries(color = "red", linewidth = 2)
m.drawstates(color = "green")
#m.drawrivers(color = "blue")
date = datetime.datetime.now(datetime.timezone.utc)
#m.nightshade(date)

#plt.show()
#plt.savefig("map.pdf")
plt.savefig("map.png")
#os.system("evince map.pdf &")
#os.system("eog map.png &")


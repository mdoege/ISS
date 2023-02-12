#!/usr/bin/env python

# ISS tracker (needs Skyfield)

import pygame
from skyfield.api import load, wgs84, utc
from daynight import get_img
import time, datetime

UPDATE = .5         # zoomed map update interval in s
UPDATETRACK = 10    # track update interval in s

bg = pygame.image.load("cities.png")
b2 = pygame.image.load("earth4k_3_bright.png")
b2 = pygame.transform.scale(b2, (1000, 500))

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

class ISS:
	def __init__(s):
		pygame.init()
		s.res = 1500, 500
		s.screen = pygame.display.set_mode(s.res)
		pygame.display.set_caption('ISS Tracker')
		s.clock = pygame.time.Clock()
		s.last = 0
		s.lasttrack = 0
		s.plot = pygame.Surface((100, 100))
		s.lpos = []

	def events(s):
		for event in pygame.event.get():
			if event.type == pygame.QUIT: s.running = False

	def run(s):
		s.running = True
		while s.running:
			s.clock.tick(10)
			s.events()
			s.update()
		pygame.quit()

	def update(s):
		# update zoomed map
		if time.time() - s.last > UPDATE:
			s.lat, s.lon = getpos()
			s.last = time.time()
			mx = int((180 + s.lon) * 8192 / 360)
			my = int(( 90 - s.lat) * 4096 / 180)
			for y in range(100):
				for x in range(100):
					try:
						c = bg.get_at(((x + mx - 50) % 8192, y + my - 50))
					except:
						c = 120, 120, 120
					s.plot.set_at((x, y), c)

		# update track data
		if time.time() - s.lasttrack > UPDATETRACK:
			s.lasttrack = time.time()
			s.lpos = []
			# calculate track for +-90 minutes:
			for x in range(-90, 91, 2):
				tnow = datetime.datetime.utcnow()
				tnow = tnow.replace(tzinfo = utc)
				td = datetime.timedelta(minutes = 1)
				t = tnow + x * td
				t = ts.from_datetime(t)
				geocentric = satellite.at(t)
				lat, lon = wgs84.latlon_of(geocentric)
				s.lpos.append((lat.degrees, lon.degrees))
			s.dn = get_img()

		out = pygame.transform.scale(s.plot, (500, 500))
		s.screen.blit(b2, (500, 0))
		s.screen.blit(s.dn, (500, 0))

		# draw track
		for n in range(0, len(s.lpos) - 1):
			l1 = int((180 + s.lpos[n][1]) * 1000 / 360) + 500
			l2 = int(( 90 - s.lpos[n][0]) *  500 / 180)
			l3 = int((180 + s.lpos[n+1][1]) * 1000 / 360) + 500
			l4 = int(( 90 - s.lpos[n+1][0]) *  500 / 180)
			if n >= len(s.lpos) // 2:
				c = (255, 255, 0)
			else:
				c = (255, 0, 0)
			if abs(l1 - l3) < 100 and abs(l2 - l4) < 100:
				pygame.draw.line(s.screen, c, (l1, l2), (l3, l4), 4)
			else:
				pygame.draw.line(s.screen, c, (l1, l2), (l3 + 1000, l4), 4)
				pygame.draw.line(s.screen, c, (l1 - 1000, l2), (l3, l4), 4)

		# draw current position
		lx = int((180 + s.lon) * 1000 / 360) + 500
		ly = int(( 90 - s.lat) *  500 / 180)
		if time.time() % 1 < .5:
			pygame.draw.rect(s.screen, (255, 0, 0), [lx - 6, ly - 6, 13, 13])

		s.screen.blit(out, (0, 0))
		pygame.display.flip()

c = ISS()
c.run()


#!/usr/bin/env python

# ISS tracker (needs Skyfield)

import pygame
from skyfield.api import load, wgs84, utc
from daynight import get_img
import time, datetime, os.path

UPDATE = .5         # zoomed map update interval in s
UPDATETRACK = 10    # track update interval in s

WIN_WIDTH = 1900                # window width
BMAPW = int(2 / 3 * WIN_WIDTH)  # big map width
ZMAPW = WIN_WIDTH - BMAPW       # zoomed map width
LWID = 4                        # line width
CSIZ = int(100 / 8192 * BMAPW)  # cursor size

bg = pygame.image.load("cities.png")
b2 = pygame.image.load("earth4k_3_bright.png")
b2 = pygame.transform.scale(b2, (BMAPW, ZMAPW))

# download new orbital elements each day
try:
	mtime = os.path.getmtime("stations.txt")
except:
	mtime = 0
if time.time() - mtime > 40000:
	update = True
else:
	update = False

# from https://rhodesmill.org/skyfield/earth-satellites.html
stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url, reload = update)
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
		s.res = ZMAPW + BMAPW, ZMAPW
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
		dt = time.time() - s.lasttrack
		if dt > UPDATETRACK or dt < 0:
			s.lasttrack = time.time()
			s.lpos = []
			# calculate track for +-90 minutes:
			for x in range(-90, 91, 2):
			    # https://blog.miguelgrinberg.com/post/it-s-time-for-a-change-datetime-utcnow-is-now-deprecated
				tnow = datetime.datetime.now(datetime.timezone.utc)
				td = datetime.timedelta(minutes = 1)
				t = tnow + x * td
				t = ts.from_datetime(t)
				geocentric = satellite.at(t)
				lat, lon = wgs84.latlon_of(geocentric)
				s.lpos.append((lat.degrees, lon.degrees))
			s.dn = get_img()
			s.dn = pygame.transform.smoothscale(s.dn, (BMAPW, ZMAPW))

		out = pygame.transform.scale(s.plot, (ZMAPW, ZMAPW))
		s.screen.blit(b2, (ZMAPW, 0))
		s.screen.blit(s.dn, (ZMAPW, 0))

		# draw track
		for n in range(0, len(s.lpos) - 1):
			l1 = int((180 + s.lpos[n][1]) * BMAPW / 360) + ZMAPW
			l2 = int(( 90 - s.lpos[n][0]) * ZMAPW / 180)
			l3 = int((180 + s.lpos[n+1][1]) * BMAPW / 360) + ZMAPW
			l4 = int(( 90 - s.lpos[n+1][0]) * ZMAPW / 180)
			if n >= len(s.lpos) // 2:
				c = (255, 255, 0)
			else:
				c = (255, 0, 0)
			if abs(l1 - l3) < BMAPW / 5 and abs(l2 - l4) < BMAPW / 5:
				pygame.draw.line(s.screen, c, (l1, l2), (l3, l4), LWID)
			else:
				pygame.draw.line(s.screen, c, (l1, l2), (l3 + BMAPW, l4), LWID)
				pygame.draw.line(s.screen, c, (l1 - BMAPW, l2), (l3, l4), LWID)

		# draw current position
		lx = int((180 + s.lon) * BMAPW / 360) + ZMAPW
		ly = int(( 90 - s.lat) * ZMAPW / 180)
		if time.time() % 1 < .5:
			pygame.draw.rect(s.screen, (255, 0, 0), [lx - CSIZ // 2, ly - CSIZ // 2, CSIZ, CSIZ])

		s.screen.blit(out, (0, 0))
		pygame.display.flip()

c = ISS()
c.run()


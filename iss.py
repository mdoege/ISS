#!/usr/bin/env python

# ISS tracker

import pygame
import json, time
from urllib.request import urlopen

bg = pygame.image.load("cities.png")
b2 = pygame.image.load("earth4k_3_bright.png")
b2 = pygame.transform.scale(b2, (1000, 500))

def getpos():
	url = "http://api.open-notify.org/iss-now.json"

	try:
		pos = urlopen(url).read()
		j = json.loads(pos)
		lat = float(j["iss_position"]["latitude"])
		lon = float(j["iss_position"]["longitude"])
	except:
		return 0, 0

	return lat, lon

class ISS:
	def __init__(s):
		pygame.init()
		s.res = 1500, 500
		s.screen = pygame.display.set_mode(s.res)
		pygame.display.set_caption('ISS Tracker')
		s.clock = pygame.time.Clock()
		s.last = 0
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
		if time.time() - s.last > 10:
			s.lat, s.lon = getpos()
			s.lpos.append((s.lat, s.lon))
			if len(s.lpos) > 100:
				s.lpos = s.lpos[-100:]
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

		out = pygame.transform.scale(s.plot, (500, 500))
		s.screen.blit(out, (0, 0))	
		s.screen.blit(b2, (500, 0))

		if s.lat != 0 or s.lon != 0:
			lx = int((180 + s.lon) * 1000 / 360) + 500
			ly = int(( 90 - s.lat) *  500 / 180)
			if time.time() % 1 < .5:
				pygame.draw.rect(s.screen, (255, 0, 0), [lx - 6, ly - 6, 13, 13])	
		for n in range(0, len(s.lpos) - 1):
			l1 = int((180 + s.lpos[n][1]) * 1000 / 360) + 500
			l2 = int(( 90 - s.lpos[n][0]) *  500 / 180)
			l3 = int((180 + s.lpos[n+1][1]) * 1000 / 360) + 500
			l4 = int(( 90 - s.lpos[n+1][0]) *  500 / 180)
			if abs(l1 - l3) < 100 and abs(l2 - l4) < 100:
				pygame.draw.line(s.screen, (255, 0, 0), (l1, l2), (l3, l4), 4)
		pygame.display.flip()

c = ISS()
c.run()


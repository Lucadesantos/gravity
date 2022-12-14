import pygame
from pygame.locals import *
import time
import sys
import math
import random
import pickle 
from colour import Color
import time

red = Color("red")
yellow = Color("yellow")
white = Color("white")
gray = Color("gray")
colors = []
colors += list(gray.range_to(red,100))
colors += list(red.range_to(yellow,1000))
colors += list(yellow.range_to(white,3000))
# Constants
WHITE = (255,255,255)
BLACK = (0,0,0)
SIZE  = (1200,600)
CENTER = [SIZE[0]/2, SIZE[1]/2]
CENTER_CONST = [SIZE[0]/2, SIZE[1]/2]

LIMIT = (10000,10000)
SCALE = 1
MAX_DISTANCE = 5000
NEW_PARTICLE_MASS = 10000
BH_MASS = 500000
G = 0.4
K = 100
toggleVect = False


def addVector(v1, v2):
	return (v1[0]+v2[0], v1[1]+v2[1])

def subVector(v1, v2):
	return (v1[0]-v2[0], v1[1]-v2[1])

def multVector(v1, v2):
	return (v1[0]*v2[0], v1[1]*v2[1])

def divVector(v1, v2):
	
	if v2[0] == 0:
		res1 = 10
	else:
		res1 = v1[0]/v2[0]
	if v2[1] == 0:
		res2 = 10
	else:
		res2 = v1[1]/v2[1]
	return (res1, res2)

def dist(x1, x2):
	return abs((math.sqrt(abs((x2[0]-x1[0]))**2+(abs(x2[1]-x1[1]))**2)))

def size(v):
	return abs(math.sqrt(v[0]**2+v[1]**2))

def drawVector(DISPLAY, universe, particle, vect, color, scale):
	global SCALE
	centeredPos = addVector(particle.pos, multVector(universe.center,(1/SCALE,1/SCALE)))
	centeredPos = multVector(centeredPos, (SCALE, SCALE))
	vstart = centeredPos
	vend = addVector(centeredPos, multVector(vect, (scale, scale)))

	pygame.draw.line(DISPLAY, color, vstart, vend, 1)


class Universe:
	particles = []
	center = []
	def __init__(self,center):
		self.center = center

	def save(self, fileName):
		with open("saves/" + fileName + ".unv", "wb") as f:
			pickle.dump(self, f)

	def fill(self, n,m):
		view_center = divVector(subVector(CENTER_CONST, self.center), (SCALE,SCALE))
		for i in range(n):
			x = random.randint(int(-CENTER_CONST[0]//SCALE),int(CENTER_CONST[0]//SCALE))
			y = random.randint(int(-CENTER_CONST[1]//SCALE),int(CENTER_CONST[1]//SCALE))
			mass = random.randint(10, m)
			velX = random.randint(-10, 10)/100
			velY = random.randint(-10, 10)/100
			self.particles.append(Particle(mass, (x,y), (velX, velY)))

	def update(self, DISPLAY):
		global toggleVect
		for particle1 in self.particles:
			vectors = []
			for particle2 in self.particles:
				if particle2 != particle1:
					distance = dist(particle1.pos, particle2.pos)
					if distance > MAX_DISTANCE:
						break
					if distance <= particle1.radius+particle2.radius:
						self.mergeParticles(particle1, particle2)
						break
					else:
						s = subVector(particle2.pos, particle1.pos)
						uVtemp = divVector(s, (distance, distance))
						F = G*(particle1.mass*particle2.mass)/distance**2
						
						uVtemp = multVector(uVtemp, (F,F))
						vectors.append(uVtemp)

			newVector = (0,0)
			for vector in vectors:
				normVect = divVector(vector, (particle1.mass**2, particle1.mass**2))				
				if toggleVect:
					drawVector(DISPLAY, self, particle1, normVect, (255,0,0), 5000)
				newVector = addVector(newVector, normVect)
			particle1.vel = addVector(particle1.vel, newVector)
			particle1.move()

			
			if abs(particle1.pos[0])>LIMIT[0] or abs(particle1.pos[1])>LIMIT[1]:
				try:
					self.particles.remove(particle1)
				except:
					pass

	def mergeParticles(self, p1, p2):
		newMass = p1.mass+p2.mass
		p1mass = multVector(p1.vel, (p1.mass,p1.mass))
		p2mass = multVector(p2.vel, (p2.mass,p2.mass))
		vel = divVector(addVector(p1mass, p2mass),(newMass*1.1,newMass*1.1))
		
		newPart = p1 if p1.mass > p2.mass else p2
		oldPart = p2 if p1.mass > p2.mass else p1
		energy = (size(p1.vel) + size(p2.vel))*(newMass)
		newPart.update(newMass, vel, energy)
	
		try:
			self.particles.remove(oldPart)
		except:
			pass
		
		
	def getParticles(self):
		return self.particles

	def addParticle(self, particle):
		self.particles.append(particle)

	def isIn(self, point):
		for particle in self.particles:
			if particle.pos[0]-particle.radius < point[0] < particle.pos[0]+particle.radius:
				if particle.pos[1]-particle.radius < point[1] < particle.pos[1]+particle.radius:
					return particle
		return None

class Particle:
	pos = ()
	vel = ()
	mass = 0
	radius = 0
	heat = 0

	def __init__(self, m, pos, vel):
		self.mass = m
		self.pos=pos
		self.vel = vel
		self.radius = round((self.mass/math.pi),2)**(1/3)
		self.heat = 0

	def update(self, m, vel, energy):
		if self.heat >=0:
			self.heat = self.heat + K*(m - self.mass)+(energy/K)
		self.mass = m
		self.vel = vel
		self.radius = round((self.mass/math.pi),2)**(1/3)
		if self.mass>BH_MASS:
			self.heat = -1

	def move(self):
		self.pos = addVector(self.pos, self.vel)
		self.heat *= 0.99999

		
def start(n, m):
	pygame.init()
	DISPLAY=pygame.display.set_mode(SIZE,0,32)

	DISPLAY.fill(BLACK)
	
	universe = Universe(CENTER)
	universe.fill(n, m)
	return DISPLAY, universe


def main(DISPLAY, universe):
	global toggleVect, SCALE
	pause = False
	pygame.font.init()
	font = pygame.font.Font("res/font.otf", 15)
	font2 = pygame.font.Font("res/font.otf", 25)
	
	dragging = False
	fast = False
	text = ""
	input_active = False
	oldTime = time.time() * 1000
	while True:

		DISPLAY.fill(BLACK)
		numParticles = len(universe.particles)
		speed = numParticles**(1/10)*0.001/50**(1/10)
		
		newTime = time.time() * 1000
		timeDelta = newTime-oldTime
		oldTime = newTime
		view_center = divVector(subVector(CENTER_CONST, universe.center), (SCALE,SCALE))
		text_surface = font.render("TPS: " + str(round(100/timeDelta,1)), False, WHITE)
		text_surface2 = font.render("(" + str(int(view_center[0])) + ":" + str(int(view_center[1])) + ") / " + str(round(SCALE,1)), False, WHITE)
		
		text_surface3 = font2.render("New save name: " + text, False, WHITE)
		text_surface4 = font2.render("PAUSED", False, WHITE)
		
		if pause or input_active:
			DISPLAY.blit(text_surface4, (SIZE[0]/2-60,5))

		DISPLAY.blit(text_surface, (5,0))
		DISPLAY.blit(text_surface2, (5,20))
		
		if input_active:
			DISPLAY.blit(text_surface3, (5,SIZE[1]-30))
		keys = pygame.key.get_pressed()
		if dragging:
			pos = multVector(pygame.mouse.get_pos(), (1/SCALE,1/SCALE))
			within.pos = subVector(pos, universe.center)


		if not fast:
			time.sleep(speed)
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos1 = pygame.mouse.get_pos()
				within = universe.isIn(subVector(pos1, universe.center))
				if within and 0:
					dragging = True
			if event.type == pygame.MOUSEBUTTONUP:
				pos2 = pygame.mouse.get_pos()
				if dragging and 0:
					dragging = False
					vel = subVector(pos2, pos1)
					within.vel = divVector(vel, (100,100))
				else:
					vel = subVector(pos2, pos1)
					newPos = subVector(view_center,multVector(subVector(CENTER_CONST,pos1),(1/SCALE,1/SCALE)))
					universe.addParticle(Particle(NEW_PARTICLE_MASS,newPos,multVector(vel, (0.01,0.01))))
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_v:
					toggleVect = not toggleVect
				if event.key == pygame.K_SPACE:
					pause = not pause
				if input_active:
					if event.key == pygame.K_RETURN:
						input_active = False
						if text != "":
							universe.save(text)
							text = ""
					elif event.key == pygame.K_BACKSPACE:
						if text == "":
							input_active = False
						text = text[:-1]
					else:
						text += event.unicode
				if event.key == pygame.K_s:
					input_active = True
				if event.key == pygame.K_f:
					fast = not fast
				if event.key == pygame.K_x:
					universe.fill(10,10000)

		if keys[pygame.K_LEFT]:
			universe.center[0] += int(2/SCALE)
		if keys[pygame.K_RIGHT]:
			universe.center[0] -= int(2/SCALE)
		if keys[pygame.K_UP]:
			universe.center[1] += int(2/SCALE)
		if keys[pygame.K_DOWN]:
			universe.center[1] -= int(2/SCALE)
		if keys[pygame.K_b]:
			SCALE -= 0.001
		if keys[pygame.K_n]:
			SCALE += 0.001
		for particle in universe.getParticles():
			centeredPos = addVector(particle.pos, multVector(universe.center,(1/SCALE,1/SCALE)))
			centeredPos = multVector(centeredPos, (SCALE, SCALE))
			
	
			pos = (particle.heat)//(K**2)
			if pos>=len(colors):
				pos = len(colors)-1
			heat = colors[int(pos)].rgb
			heat = (255*heat[0],255*heat[1],255*heat[2])
			w=0
			if particle.mass > BH_MASS:
				heat = (50,50,50)
				pygame.draw.circle(DISPLAY,(255,255,255),centeredPos,particle.radius*SCALE, 2)	
				pygame.draw.circle(DISPLAY,heat,centeredPos,(particle.radius**0.5)*SCALE)
			else:
				pygame.draw.circle(DISPLAY,heat,centeredPos,particle.radius*SCALE)
			if toggleVect:
				drawVector(DISPLAY, universe, particle, particle.vel, (0,255,0), 50)
			
		if not (pause or input_active):
			universe.update(DISPLAY)
		pygame.display.update()


if len(sys.argv)>1:
	if sys.argv[1].isdigit():
		maxMass = 200
		if len(sys.argv)>2 and sys.argv[2].isdigit():
			maxMass = int(sys.argv[2])
		DISPLAY, universe = start(int(sys.argv[1]), maxMass)
	else:	
		DISPLAY, universe = start(0, 0)
		with open("saves/" + sys.argv[1] + ".unv", "rb") as f:
			universe = pickle.load(f)
else:
	DISPLAY, universe = start(50, 200)

main(DISPLAY, universe)
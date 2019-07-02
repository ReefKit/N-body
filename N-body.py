import sys
from random import random, uniform
import math
from time import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import configparser
from astropy.time import Time as astrotime
import datetime
import threading
from PIL import Image as Image
import numpy
import json

config = configparser.ConfigParser()
config.read('configure.ini')


WIDTH = int(config['CONFIGURE']['WIDTH'])
HEIGHT = int(config['CONFIGURE']['HEIGHT'])
POINT_SIZE = float(config['CONFIGURE']['POINT_SIZE'])
POSITION_X = int(config['CONFIGURE']['POSITION_X'])
POSITION_Y = int(config['CONFIGURE']['POSITION_Y'])
WORLD_LEFT = float(config['CONFIGURE']['WORLD_LEFT'])
WORLD_RIGHT = float(config['CONFIGURE']['WORLD_RIGHT'])
WORLD_BOTTOM = float(config['CONFIGURE']['WORLD_BOTTOM'])
WORLD_TOP = float(config['CONFIGURE']['WORLD_TOP'])
VIEW_ANGLE = float(config['CONFIGURE']['VIEW_ANGLE'])
RHO = float(config['CONFIGURE']['RHO'])
WORLD_NEAR = float(config['CONFIGURE']['WORLD_NEAR'])
WORLD_FAR = float(config['CONFIGURE']['WORLD_FAR'])
SCALE = float(config['CONFIGURE']['SCALE'])
BALL_SIZE = float(config['CONFIGURE']['BALL_SIZE'])
REFRESH_RATE = float(config['CONFIGURE']['REFRESH_RATE'])
LINE_SIZE = float(config['CONFIGURE']['LINE_SIZE'])
GRAV_CONS = float(config['CONFIGURE']['GRAV_CONS']) * 1E-9 #Convert meter cubed to kilometer cubed
NORM_DELTA_T = float(config['CONFIGURE']['NORM_DELTA_T'])
FINE_DELTA_T = float(config['CONFIGURE']['FINE_DELTA_T'])
SEC_PER_DAY = float(config['CONFIGURE']['SEC_PER_DAY'])
EXPONENT = float(config['CONFIGURE']['EXPONENT'])
ORBIT_LENGTH = int(config['CONFIGURE']['ORBIT_LENGTH'])
SAVE_RATE = int(config['CONFIGURE']['SAVE_RATE'])
TEXTURE_PATH = str(config['CONFIGURE']['TEXTURE_PATH'])



'''
Class holds attributes of a single body
'''
class Body(object):
	global_ident = 0
	def __init__(self, ident=None, time=2452170.375, x=None, y=None,z=None,Vx=None,Vy=None,Vz=None,mass=None,radius=None,color=None,texture_file=None):
		if ident == None:
			self.ident = Body.global_ident
			Body.global_ident += 1
		else:
			self.ident = ident
		self.time = time
		self.x = x or random()
		self.y = y or random()
		self.z = z or random()
		self.Vx = Vx or random()
		self.Vy = Vy or random()
		self.Vz = Vz or random()
		self.mass = mass or random()
		self.radius = radius or random()
		self.parse_color(color)
		self.texture = None
		self.load_texture(texture_file)
		self.coord = []
		self.zeroF()
		self.collisions = ""

	def zeroF(self):
		self.Fx = 0
		self.Fy = 0
		self.Fz = 0

	def __str__(self):
		return (
			f"ident = {self.ident}, "
			f"time = {self.time} = {astrotime(self.time, format = 'jd', scale = 'utc').isot}, "
			f"x = {self.x}, "
			f"y = {self.y}, "
			f"z = {self.z}, "
			f"Vx = {self.Vx}, "
			f"Vy = {self.Vy}, "
			f"Vz = {self.Vz}, "
			f"mass = {self.mass}, "
			f"radius = {self.radius}, "
			f"color = {'%02X%02X%02X' % self.color}")

	def cal_netforce(self, other_body):
		Dx = other_body.x - self.x
		Dy = other_body.y - self.y
		Dz = other_body.z - self.z
		distance = math.sqrt(Dx**2 + Dy**2 + Dz**2)
		con = GRAV_CONS * self.mass * other_body.mass / (distance**2)
		gd = con / distance
		self.Fx += gd * Dx
		self.Fy += gd * Dy
		self.Fz += gd * Dz

	def cal_velocity(self):
		self.Vx += self.Fx * planet_system.DELTA_T / self.mass
		self.Vy += self.Fy * planet_system.DELTA_T / self.mass
		self.Vz += self.Fz * planet_system.DELTA_T / self.mass

	def cal_position(self):
		self.x += self.Vx * planet_system.DELTA_T
		self.y += self.Vy * planet_system.DELTA_T
		self.z += self.Vz * planet_system.DELTA_T
		self.coord.append((self.x,self.y,self.z))

	def parse_color(self, color):
		if not color:
			self.color = (random(), random(), random())
		else:
			self.color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

	def load_texture(self, filename):
		if not filename:
			return
		textID = glGenTextures(1)
		img = Image.open(TEXTURE_PATH + filename)
		img_data = numpy.array(list(img.getdata()), numpy.int8)
		glBindTexture(GL_TEXTURE_2D, textID)
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
			 GL_RGB, GL_UNSIGNED_BYTE, img_data)
		self.texture = textID

	def display(self):
		if self.texture:
			''''''

			qobj = gluNewQuadric()
			gluQuadricTexture(qobj, GL_TRUE)
			gluQuadricDrawStyle(qobj, GLU_FILL)
			gluQuadricNormals(qobj, GLU_SMOOTH)
			#gluQuadricOrientation()
			glBindTexture(GL_TEXTURE_2D, self.texture)
			glEnable(GL_TEXTURE_2D)
			gluSphere(qobj, init.BALL_SIZE * (self.radius**init.EXPONENT), 50, 50)
			gluDeleteQuadric(qobj)
			glDisable(GL_TEXTURE_2D)
			'''
			glEnable(GL_TEXTURE_2D)
			glBindTexture(GL_TEXTURE_2D, self.texture)
			glEnable(GL_TEXTURE_GEN_S)
			glEnable(GL_TEXTURE_GEN_T)
			glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
			glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
			glutSolidSphere(BALL_SIZE * (self.radius**init.EXPONENT), 50, 50)
			glDisable(GL_TEXTURE_2D)
			'''
		else:
			'''
			glColor3f(self.color[0]/255, self.color[1]/255, self.color[2]/255)
			glutSolidSphere(BALL_SIZE * (body.radius**init.EXPONENT), 20, 20)
			glPopMatrix()
			glLineWidth(1)
			glColor(self.color[0]/255, self.color[1]/255, self.color[2]/255)
			'''
			color = [self.color[0]/255, self.color[1]/255, self.color[2]/255]
			glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
			glutSolidSphere(BALL_SIZE * (self.radius**init.EXPONENT), 20, 20)
'''
Class holds bodies
'''
class Asystem:
	def __init__(self,input):
		self.DELTA_T = NORM_DELTA_T
		if type(input) == int:
			self.n_bodies = input
			self.system = []
			for i in range(self.n_bodies):
				self.system.append(Body())
		elif type(input) == str:
			self.system = self.read_from_file(input)
		else:
			raise Exception("Invalid input type for init of Asystem")
		self.count = 0
		self.closeness = []
	def __str__(self):
		return "\n".join([str(body) for body in self.system])

	def read_from_file(self,file_name):
		bodies = []
		with open(file_name) as file:
			for body_json in json.load(file):
				body = Body(body_json.get("ident"),
							body_json.get("JDTDB"),
							body_json.get("X (km)"),
							body_json.get("Y (km)"),
							body_json.get("Z (km)"),
							body_json.get("VX (km/s)"),
							body_json.get("VY (km/s)"),
							body_json.get("VZ (km/s)"),
							body_json.get("mass (kg)"),
							body_json.get("radius (km)"),
							body_json.get("color"),
							body_json.get("texture"))
				bodies.append(body)
		return bodies

	def write_to_file(self,file):
		data = ''
		for body in self.system:
			body_data = (
			f"{body.ident}, "
			f"{body.time}, "
			f"{body.x}, "
			f"{body.y}, "
			f"{body.z}, "
			f"{body.Vx}, "
			f"{body.Vy}, "
			f"{body.Vz}, "
			f"{body.mass}, "
			f"{body.radius}, "
			f"{'%02X%02X%02X' % body.color}, "
			f"{body.texture}\n"
			)
			data += body_data
		data += f"Collisions: {self.collisions}\n"
		close_list = ", ".join(self.closeness)
		data += "Closeness: " + close_list + '\n\n'
		file.write(data)

	def compute1(self,body):

		body.zeroF()
		for other_body in self.system:
			if body != other_body:
				body.cal_netforce(other_body)
		body.cal_velocity()

	def compute2(self,body):
		body.cal_position()
		body.time += self.DELTA_T / SEC_PER_DAY

	def if_collision(self):
		self.collisions = ""
		if_T = False
		for i in range(len(self.system)):
			for j in range(i):
				x_dif = self.system[i].x - self.system[j].x
				y_dif = self.system[i].y - self.system[j].y
				z_dif = self.system[i].z - self.system[j].z
				distance = (x_dif**2 + y_dif**2 + z_dif**2)**0.5
				if_T = distance <= 30*(self.system[i].radius + self.system[j].radius)
				if distance <= self.system[i].radius + self.system[j].radius:
					self.collisions += f"{self.system[i].ident} and {self.system[j].ident}, "
		if self.collisions != "":
			string = self.collisions[:-2]
		else:
			string = "None"
		self.glut_print(10, 25, GLUT_BITMAP_9_BY_15, "Collision: " + string, 1.0, 1.0, 1.0, 1.0)
		if init.bool_T == False:
			planet_system.DELTA_T = 0
		elif if_T == True:
			self.DELTA_T = FINE_DELTA_T
			self.write_to_file(write_file)
		else:
			self.DELTA_T = init.NORM_DELTA_T

	'''
	This function redraws the screen after the positions of particles have been updated
	'''
	def display(self):

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(init.eyeRho * math.sin(init.eyePhi) * math.sin(init.eyeTheta),
				  init.eyeRho * math.cos(init.eyePhi),
				  init.eyeRho * math.sin(init.eyePhi) * math.cos(init.eyeTheta),
				  init.look[0], init.look[1], init.look[2],
				  0, init.upY, 0)
		light_sun_position = [planet_system.system[0].x,planet_system.system[0].y,planet_system.system[0].z]
		glLightfv(GL_LIGHT0, GL_POSITION, light_sun_position)

		self.glut_print(10, 10, GLUT_BITMAP_9_BY_15, astrotime(self.system[0].time, format = 'jd').iso, 1.0, 1.0, 1.0, 1.0)
		self.if_collision()
		if init.display:
			for body in self.system:
				glPushMatrix()
				glTranslated(init.SCALE * body.x, init.SCALE * body.y, init.SCALE * body.z)
				#glRotatef((-1)*init.eyeRho * math.sin(init.eyePhi) * math.sin(init.eyeTheta), 1, 0, 0)
				#glRotatef((-1)*init.eyeRho * math.cos(init.eyePhi), 0, 1, 0)
				#glRotatef((-1)*init.eyeRho * math.sin(init.eyePhi) * math.sin(init.eyeTheta), 0, 0, 1)
				body.display()
				glPopMatrix()

				glDisable(GL_LIGHTING)
				glLineWidth(1)
				glColor3f(body.color[0]/255, body.color[1]/255, body.color[2]/255)
				if init.orbit == True:
					glBegin(GL_LINE_STRIP)
					dis_coord = body.coord
					if init.short_orbit:

						if len(dis_coord)>ORBIT_LENGTH:
							dis_coord = dis_coord[(-1)*ORBIT_LENGTH:]
					for point in dis_coord:
						glVertex3f(init.SCALE * point[0], init.SCALE * point[1], init.SCALE * point[2])
					glEnd()
				self.glut_print3(init.SCALE * body.x, init.SCALE * body.y, init.SCALE * body.z, GLUT_BITMAP_9_BY_15, body.ident, body.color[0]/255, body.color[1]/255, body.color[2]/255, 1.0)
				glEnable(GL_LIGHTING)

		glutSwapBuffers()

	'''
	Display text
	'''
	def glut_print(self, x, y, font, text, r, g, b, a):
		self.blending = False
		if glIsEnabled(GL_BLEND):
			self.blending = True

		glEnable(GL_BLEND)
		glColor3f(r, g, b)
		glWindowPos2f(x, y)
		for ch in str(text):
			glutBitmapCharacter(font, ctypes.c_int(ord(ch)))

		if not self.blending:
			glDisable(GL_BLEND)

	def glut_print3(self, x, y, z, font, text, r, g, b, a):
		self.blending = False
		if glIsEnabled(GL_BLEND):
			self.blending = True

		glEnable(GL_BLEND)
		glColor3f(r, g, b)
		glRasterPos3f(x, y, z)
		for ch in str(text):
			glutBitmapCharacter(font, ctypes.c_int(ord(ch)))

		if not self.blending:
			glDisable(GL_BLEND)
	'''
	Calculates when bodies reach a closest proximity
	If the distance is smaller than the distance of the previous and next time step, its recorded
	'''
	def close_calc(self,body1,body2):
		distances = []
		if len(body1.coord)>2:
			for i in range(1,4):
				x_dif = body1.coord[-i][0] - body2.coord[-i][0]
				y_dif = body1.coord[-i][1] - body2.coord[-i][1]
				z_dif = body1.coord[-i][2] - body2.coord[-i][2]
				distances.append((x_dif ** 2 + y_dif ** 2 + z_dif ** 2) ** 0.5)
			if distances[0] > distances[1] and distances[1] < distances[2]:
				self.closeness.append(body1.ident + " and " + body2.ident + "; " + str(distances[1]))
				return True
		return False

	def animate(self):
		self.closeness = []
		#if self.close_calc(self.system[11], self.system[3]):
		#	self.write_to_file(write_file)
		if self.count % SAVE_RATE == 0:
			self.write_to_file(write_file)
		calc1 = []
		for body in self.system:
			calc1.append(threading.Thread(target=self.compute1, args=(body,)))
			calc1[-1].start()
		for i in calc1:
			i.join()
		calc2 = []
		for body in self.system:
			calc2.append(threading.Thread(target=self.compute2, args=(body,)))
			calc2[-1].start()
		for i in calc2:
			i.join()

		self.display()
		self.count+=1



class Definition:
	def __init__(self):			 #InitialiglEnable(GL_CULL_FACE)zation of graphics
		glClearColor(0.1,0.0,0.15,0.0)
		glPointSize(POINT_SIZE)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glShadeModel(GL_SMOOTH)

		glEnable(GL_CULL_FACE)
		glEnable(GL_LIGHTING)
		glEnable(GL_DEPTH_TEST)

		mat_specular = (1.0, 1.0, 1.0, 1.0)
		mat_shininess = (50)
		light_position = (1.0, 1.0, 1.0, 0.0)
		lightZeroPosition = [10., 4., 10., 1.]
		light_sun_position = [planet_system.system[0].x,planet_system.system[0].y,planet_system.system[0].z]
		glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
		glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
		lightZeroColor = [1.0, 1.0, 1.0, 1.0]
		#glLightfv(GL_LIGHT0, GL_POSITION, light_sun_position)
		#glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
		#glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
		#glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
		glEnable(GL_LIGHT0)

		#global previousTime, eyeTheta, eyePhi, eyeRho, look, windowWidth, windowHeight, upY
		self.displayRatio = 1 * WIDTH / HEIGHT
		self.windowWidth = WIDTH
		self.windowHeight = HEIGHT
		self.previousTime = time()
		self.eyeTheta = 0
		self.eyePhi = math.pi * 0.5
		self.eyeRho = RHO
		self.upY = 1
		self.look = [0, 0, 0]
		self.SCALE = SCALE
		self.EXPONENT = EXPONENT
		self.button = None
		self.state = None
		self.bool_T = True
		self.orbit = True
		self.display = True
		self.ORBIT_LENGTH = ORBIT_LENGTH
		self.short_orbit = True
		self.NORM_DELTA_T = NORM_DELTA_T
		self.BALL_SIZE = BALL_SIZE
		gluPerspective(VIEW_ANGLE, self.displayRatio, WORLD_NEAR, WORLD_FAR)
		glutKeyboardFunc(self.keyboard)
		glutMouseFunc(self.mouse)
		glutMotionFunc(self.motion)
		glutReshapeFunc(self.reshape)

	def keyboard(self, theKey, mouseX, mouseY): #Manipulate with the image
		if (theKey == b'x' or theKey == b'X'):
			sys.exit()
		if (theKey == b'i' or theKey == b'I'):
			self.eyePhi -= math.pi / 20
		if (theKey == b'0'):
			self.eyePhi = 2 * math.pi
		elif (theKey == b'o' or theKey == b'O'):
			self.eyePhi += math.pi / 20
		elif (theKey == b'j' or theKey == b'J'):
			self.eyeTheta -= math.pi / 20
		elif (theKey == b'k' or theKey == b'K'):
			self.eyeTheta += math.pi / 20
		elif (theKey == b'n' or theKey == b'N'):
			self.eyeRho *= 1.1
		elif (theKey == b'm' or theKey == b'M'):
			self.eyeRho /= 1.1
		elif (theKey == b'w' or theKey == b'W'):
			self.look[1] += 0.01 * self.SCALE * self.eyeRho
		elif (theKey == b's' or theKey == b'S'):
			self.look[1] -= 0.01 * self.SCALE * self.eyeRho
		elif (theKey == b'a' or theKey == b'A'):
			self.look[0] -= 0.01 * self.SCALE * self.eyeRho
		elif (theKey == b'd' or theKey == b'D'):
			self.look[0] += 0.01 * self.SCALE * self.eyeRho
		elif (theKey == b'e' or theKey == b'E'):
			self.SCALE *= 1.1
		elif (theKey == b'q' or theKey == b'Q'):
			self.SCALE *= .9
		elif (theKey == b','):
			self.EXPONENT *= 1.01
		elif (theKey == b'.'):
			self.EXPONENT *= 0.99
		if (theKey == b' '):
			self.bool_T = not self.bool_T
		elif (theKey == b'1'):
			self.orbit = not self.orbit
		elif (theKey == b'2'):
			self.display = not self.display
		elif (theKey == b'3'):
			self.short_orbit = not self.short_orbit
		elif (theKey == b'='):
			self.ORBIT_LENGTH+=10
		elif (theKey == b'-'):
			self.ORBIT_LENGTH-=10
			if self.ORBIT_LENGTH <= 0:
				self.ORBIT_LENGTH+=10
		elif (theKey == b'['):
			self.NORM_DELTA_T/=1.1
		elif (theKey == b']'):
			self.NORM_DELTA_T*=1.1
		elif (theKey == b'r'):
			self.BALL_SIZE/=1.1
		elif (theKey == b't'):
			self.BALL_SIZE*=1.1
		self.prevMouseX = mouseX
		self.prevMouseY = mouseY

		if math.sin(self.eyePhi) > 0: self.upY = 1
		else: self.upY = -1

	def mouse(self, button, state, mouseX, mouseY):
		self.button = button
		self.state = state
		self.prevMouseX = mouseX
		self.prevMouseY = mouseY

	def motion(self,mouseX,mouseY):
		try:
			x_change = mouseX - self.prevMouseX
		except:
			x_change = 0
		try:
			y_change = mouseY - self.prevMouseY
		except:
			y_change = 0
		if self.button == GLUT_LEFT_BUTTON and self.state == GLUT_DOWN:
			self.eyePhi -= y_change / 300
			self.eyeTheta -= x_change / 300
		elif self.button == GLUT_RIGHT_BUTTON and self.state == GLUT_DOWN:
			self.look[1] += 0.0002 * y_change * self.SCALE * self.eyeRho
			self.look[0] -= 0.0002 * x_change * self.SCALE * self.eyeRho
		if (self.button == GLUT_LEFT_BUTTON and self.state == GLUT_UP) or (self.button == GLUT_RIGHT_BUTTON and self.state == GLUT_UP):
			self.prevMouseX = None
			self.prevMouseY = None
		else:
			self.prevMouseX = mouseX
			self.prevMouseY = mouseY

	def reshape(self, width, height):			 #Manipulate with the window
		self.displayRatio = 1 * width / height
		self.windowWidth = width
		self.windowHeight = height
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(VIEW_ANGLE, self.displayRatio, WORLD_NEAR, WORLD_FAR)
		glViewport(0, 0, self.windowWidth, self.windowHeight)



'''
Randomly generates planetary system
'''
def planet_system(n_bodies):
	system = Asystem(0)
	system.system.append(Body(0,2452170.375,0,0,0,0,0,0,100000000000000000000,3,253,184,19, 0))
	position = 5
	velocity = 1
	for i in range(n_bodies):
		if i != 0:
			mass_radius = uniform(1,2000000000000)
			system.system.append(Body(i,2452170.375,uniform(-1 * position,position),uniform(-1 * position,position),uniform(-1 * position,position),uniform(-1 * velocity,velocity),uniform(-1 * velocity,velocity),uniform(-1 * velocity,velocity),mass_radius,mass_radius/1000000000000,uniform(0,255),uniform(0,255),uniform(0,255),0))
	return system



if __name__ == "__main__":
	with open(f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ (validity)')}.csv", 'w') as write_file:
		write_file.write('ident,			 JDTDB,					  X,					  Y,					  Z,			  VX (km/s),			  VY (km/s),			  VZ (km/s),			 mass (kg),		  radius (km),  color,\n')

		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowSize(WIDTH, HEIGHT)
		glutInitWindowPosition(POSITION_X, POSITION_Y)
		glutCreateWindow("N-Body")


		glGenTextures(1)
		#planet_system = planet_system(10)
		planet_system = Asystem("Solar_system.json")

		init = Definition()

		if init.display:
			glutDisplayFunc(planet_system.display)
		glutIdleFunc(planet_system.animate)

		glutMainLoop()

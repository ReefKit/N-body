"""
N-body Simulation

Usage:
    python N-body.py                     # Runs the solar system simulation
    python N-body.py random [N]          # Runs a random simulation with N bodies (default: 10)
    python N-body.py random-star [N]     # Runs a random simulation with N bodies and a central star (default: 10)

Description:
    This program simulates an N-body system using OpenGL for visualization.
    It supports three modes:
    - Solar system mode (default) using predefined celestial data from 'Solar_system.csv'.
    - Random mode generating N bodies with no specific structure.
    - Random-star mode generating N bodies with a central star.

Configuration:
    - 'config/configure.ini' is used for the solar system mode.
    - 'config/configure_random.ini' is used for both the random and random-star modes.

Output:
    - A CSV file containing the simulation data is generated for analysis.
"""

import sys
import os
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

# Load configuration settings based on mode selection
SOLAR_SYSTEM_FILE = "data/Solar_system.csv"
RANDOM_CONFIG_FILE = "config/configure_random.ini"
SOLAR_CONFIG_FILE = "config/configure.ini"

config = configparser.ConfigParser()
if len(sys.argv) > 1 and sys.argv[1] == "random":
    config.read(RANDOM_CONFIG_FILE)
    system_mode = "random"
    num_bodies = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
elif len(sys.argv) > 1 and sys.argv[1] == "random-star":
    config.read(RANDOM_CONFIG_FILE)  # Uses the same config as random mode
    system_mode = "random-star"
    num_bodies = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
else:
    config.read(SOLAR_CONFIG_FILE)
    system_mode = "solar"

# Screen and world settings
WIDTH = int(config['CONFIGURE']['WIDTH'])
HEIGHT = int(config['CONFIGURE']['HEIGHT'])
POINT_SIZE = int(config['CONFIGURE']['POINT_SIZE'])
POSITION_X = int(config['CONFIGURE']['POSITION_X'])
POSITION_Y = int(config['CONFIGURE']['POSITION_Y'])
VIEW_ANGLE = float(config['CONFIGURE']['VIEW_ANGLE'])
BALL_SIZE = float(config['CONFIGURE']['BALL_SIZE'])
REFRESH_RATE = float(config['CONFIGURE']['REFRESH_RATE'])

# World boundaries
WORLD_LEFT = float(config['CONFIGURE']['WORLD_LEFT'])
WORLD_RIGHT = float(config['CONFIGURE']['WORLD_RIGHT'])
WORLD_BOTTOM = float(config['CONFIGURE']['WORLD_BOTTOM'])
WORLD_TOP = float(config['CONFIGURE']['WORLD_TOP'])
RHO = float(config['CONFIGURE']['RHO'])
WORLD_NEAR = float(config['CONFIGURE']['WORLD_NEAR'])
WORLD_FAR = float(config['CONFIGURE']['WORLD_FAR'])
SCALE = float(config['CONFIGURE']['SCALE'])
LINE_SIZE = float(config['CONFIGURE']['LINE_SIZE'])

# Simulation constants
GRAV_CONS = float(config['CONFIGURE']['GRAV_CONS']) * 1E-9  # Convert meter cubed to kilometer cubed
NORM_DELTA_T = float(config['CONFIGURE']['NORM_DELTA_T'])
FINE_DELTA_T = float(config['CONFIGURE']['FINE_DELTA_T'])
SEC_PER_DAY = float(config['CONFIGURE']['SEC_PER_DAY'])
EXPONENT = float(config['CONFIGURE']['EXPONENT'])
ORBIT_LENGTH = int(config['CONFIGURE']['ORBIT_LENGTH'])
SAVE_RATE = int(config['CONFIGURE']['SAVE_RATE'])
TEXTURE_FILE = str(config['CONFIGURE']['TEXTURE_FILE'])


class Body(object):
    """Represents a celestial body in the simulation."""
    
    global_ident = 0
    
    def __init__(self, ident=None, time=None, x=None, y=None, z=None, Vx=None, Vy=None, Vz=None,
                 mass=None, radius=None, color1=None, color2=None, color3=None, texture=None):
        """Initializes a celestial body with position, velocity, mass, and appearance."""
        
        if ident is None:
            self.ident = Body.global_ident
            Body.global_ident += 1
        else:
            self.ident = ident
        self.time = time if time is not None else 2452170.375  # Default timestamp
        self.x = x if x is not None else random()
        self.y = y if y is not None else random()
        self.z = z if z is not None else random()
        self.Vx = Vx if Vx is not None else random()
        self.Vy = Vy if Vy is not None else random()
        self.Vz = Vz if Vz is not None else random()
        self.mass = mass if mass is not None else uniform(1e22, 1e30)
        self.radius = radius if radius is not None else 1.0
        self.color1 = color1 if color1 is not None else random()
        self.color2 = color2 if color2 is not None else random()
        self.color3 = color3 if color3 is not None else random()
        self.texture = texture if texture is not None else 0
        self.coord = []
        self.zeroF()
        self.collisions = ""

    def zeroF(self):
        """Resets force components to zero before computing new forces in the next simulation step."""

        self.Fx = 0
        self.Fy = 0
        self.Fz = 0

    def print(self):
        """Prints details of the body for debugging purposes."""
        
        print("ident = " + str(self.ident)
              + ", time =  " + str(self.time) + " = " + str(astrotime(self.time, format = "jd", scale = 'utc').isot)
              + ", x = " + str(self.x)
              + ", y = " + str(self.y)
              + ", z = " + str(self.z)
              + ", Vx = " + str(self.Vx)
              + ", Vy = " + str(self.Vy)
              + ", Vz = " + str(self.Vz)
              + ", mass = " + str(self.mass)
              + ", radius = " + str(self.radius)
              + ", color1 = " + str(self.color1)
              + ", color2 = " + str(self.color2)
              + ", color3 = " + str(self.color3))

    def cal_netforce(self, other_body):
        """Computes the net gravitational force acting on this body due to all others."""
        
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
        """Updates velocity based on calculated forces."""
        
        self.Vx += self.Fx * planet_system.DELTA_T / self.mass
        self.Vy += self.Fy * planet_system.DELTA_T / self.mass
        self.Vz += self.Fz * planet_system.DELTA_T / self.mass

    def cal_position(self):
        """Updates position based on current velocity."""
        
        self.x += self.Vx * planet_system.DELTA_T
        self.y += self.Vy * planet_system.DELTA_T
        self.z += self.Vz * planet_system.DELTA_T
        self.coord.append((self.x,self.y,self.z))

    def display(self):
        """Handles OpenGL rendering for this celestial body."""
        
        if self.texture != 0:
            ''''''

            qobj = gluNewQuadric()
            gluQuadricTexture(qobj, GL_TRUE)
            gluQuadricDrawStyle(qobj, GLU_FILL)
            gluQuadricNormals(qobj, GLU_SMOOTH)
            #gluQuadricOrientation()
            glBindTexture(GL_TEXTURE_2D, planet_system.texture_names[self.texture-1])
            glEnable(GL_TEXTURE_2D)
            gluSphere(qobj, init.BALL_SIZE * (self.radius**init.EXPONENT), 50, 50)
            gluDeleteQuadric(qobj)
            glDisable(GL_TEXTURE_2D)
            '''
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, planet_system.texture_names[self.texture-1])
            glEnable(GL_TEXTURE_GEN_S)
            glEnable(GL_TEXTURE_GEN_T)
            glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
            glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
            glutSolidSphere(BALL_SIZE * (self.radius**init.EXPONENT), 50, 50)
            glDisable(GL_TEXTURE_2D)
            '''
        else:
            '''
            glColor3f(self.color1/255, self.color2/255, self.color3/255)
            glutSolidSphere(BALL_SIZE * (body.radius**init.EXPONENT), 20, 20)
            glPopMatrix()
            glLineWidth(1)
            glColor(self.color1/255,self.color2/255,self.color3/255)
            '''
            color = [self.color1/255, self.color2/255, self.color3/255]
            glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
            glutSolidSphere(BALL_SIZE * (self.radius**init.EXPONENT), 20, 20)

class Asystem:
    """Handles a system of multiple celestial bodies"""
    
    def __init__(self,input):
        """Initializes a planetary system from a file or generates a random one."""
        
        self.DELTA_T = NORM_DELTA_T
        self.collisions = ""
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
        self.texture_names = self.create_textures()
        self.closeness = []
        
    def print(self):
        """Prints details of all bodies in the system."""
        
        for body in self.system:
            body.print()

    def read_from_file(self,file_name):
        """Loads a system configuration from a CSV file."""
        
        bodies = []
        for line in open(file_name):
            fields = line.split(",")
            if fields[0] != 'ident':
                body = Body(str(fields[0]),
                            float(fields[1]),
                            float(fields[2]),
                            float(fields[3]),
                            float(fields[4]),
                            float(fields[5]),
                            float(fields[6]),
                            float(fields[7]),
                            float(fields[8]),
                            float(fields[9]),
                            float(fields[10]),
                            float(fields[11]),
                            float(fields[12]),
                            int(fields[13]))
                bodies.append(body)
        return bodies

    def write_to_file(self,file):
        """Saves the current system state to a file."""
        
        data = ''
        for body in self.system:
            body_data = (str(body.ident) + ", "
                         + str(body.time) + ", "
                         + str(body.x) + ", "
                         + str(body.y) + ", "
                         + str(body.z) + ", "
                         + str(body.Vx) + ", "
                         + str(body.Vy) + ", "
                         + str(body.Vz) + ", "
                         + str(body.mass) + ", "
                         + str(body.radius) + ", "
                         + str(body.color1) + ", "
                         + str(body.color2) + ", "
                         + str(body.color3) + ", "
                         + str(body.texture) + "\n")
            data += body_data
        data += "Collisions: " + self.collisions + '\n'
        close_list = ""
        for i in self.closeness:
            close_list+= i + ", "
        if close_list != []:
            close_list = close_list[:-2]
        data += "Closeness: " + close_list + '\n\n'
        file.write(data)

    def compute1(self,body):
        """Computes the gravitational forces on a given body due to all other bodies and updates its velocity."""

        body.zeroF()
        for other_body in self.system:
            if body != other_body:
                body.cal_netforce(other_body)
        body.cal_velocity()

    def compute2(self,body):
        """Updates the position of the body based on its velocity and increments the simulation time."""
        
        body.cal_position()
        body.time += self.DELTA_T / SEC_PER_DAY

    def if_collision(self):
        """Detects collisions between bodies, logs them, and adjusts the time step to be more fine."""
        
        self.collisions = ""
        if_T = False
        for i in range(len(self.system)):
            for j in range(len(self.system)):
                if i > j:
                    x_dif = self.system[i].x - self.system[j].x
                    y_dif = self.system[i].y - self.system[j].y
                    z_dif = self.system[i].z - self.system[j].z
                    distance = (x_dif**2 + y_dif**2 + z_dif**2)**0.5
                    if distance <= 30*(self.system[i].radius + self.system[j].radius):
                        if_T = True
                    if distance <= self.system[i].radius + self.system[j].radius:
                        self.collisions += str(self.system[i].ident) + " and " + str(self.system[j].ident) + ", "
        if self.collisions != "":
            string = self.collisions[:-2]
            self.glut_print(10, 25, GLUT_BITMAP_9_BY_15, "Collision: " + string, 1.0, 1.0, 1.0, 1.0)
        else:
            self.glut_print(10, 25, GLUT_BITMAP_9_BY_15, "Collision: None", 1.0, 1.0, 1.0, 1.0)
        if init.bool_T == False:
            planet_system.DELTA_T = 0
        elif if_T == True:
            self.DELTA_T = FINE_DELTA_T
            self.write_to_file(write_file)
        else:
            self.DELTA_T = init.NORM_DELTA_T

    def create_textures(self):
        """Loads and applies texture images for rendering."""
        
        filename = []
        file = open(f"config/{TEXTURE_FILE}", 'r')

        try:
            for line in file:
                newline = line.split('\n')
                filename.append(newline[0])
        except:
            print("%s not found" %TEXTURE_FILE)
        if len(filename)>0:
            textID = []
            for i in range(len(filename)):
                textID.append(glGenTextures(1))
            for i in range(len(filename)):
                img = Image.open(filename[i])
                img_data = numpy.array(list(img.getdata()), numpy.int8)
                glBindTexture(GL_TEXTURE_2D, textID[i])
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
            return(textID)
    
    def display(self):
        """Renders the planetary system, applying transformations, lighting, and drawing orbits."""

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
                glColor3f(body.color1/255, body.color2/255, body.color3/255)
                if init.orbit == True:
                    glBegin(GL_LINE_STRIP)
                    dis_coord = body.coord
                    if init.short_orbit:

                        if len(dis_coord)>ORBIT_LENGTH:
                            dis_coord = dis_coord[(-1)*ORBIT_LENGTH:]
                    for point in dis_coord:
                        glVertex3f(init.SCALE * point[0], init.SCALE * point[1], init.SCALE * point[2])
                    glEnd()
                self.glut_print3(init.SCALE * body.x, init.SCALE * body.y, init.SCALE * body.z, GLUT_BITMAP_9_BY_15, body.ident, body.color1/255, body.color2/255, body.color3/255, 1.0)
                glEnable(GL_LIGHTING)
        
        # Render text for controls
        self.render_controls()
        
        glutSwapBuffers()

    def glut_print(self, x, y, font, text, r, g, b, a):
        """Renders 2D text at the specified screen position in OpenGL."""

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
        """Renders 3D text in OpenGL at the given world coordinates."""

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

    def close_calc(self,body1,body2):
        """Checks if two bodies are at their closest approach and records the event."""

        distances = []
        global bool
        bool = False
        if len(body1.coord)>2:
            for i in range(0,4):
                if i != 0:
                    x_dif = body1.coord[-i][0] - body2.coord[-i][0]
                    y_dif = body1.coord[-i][1] - body2.coord[-i][1]
                    z_dif = body1.coord[-i][2] - body2.coord[-i][2]
                    distances.append((x_dif ** 2 + y_dif ** 2 + z_dif ** 2) ** 0.5)
            if distances[0] > distances[1] and distances[1] < distances[2]:
                self.closeness.append(body1.ident + " and " + body2.ident + "; " + str(distances[1]))
                bool=True
        return bool

    def animate(self):
        """Manages threading for force calculations, updates body positions, and calls rendering."""

        self.closeness = []
        #if self.close_calc(self.system[11], self.system[3]):
        #    self.write_to_file(write_file)
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
        
    def render_controls(self):
        """Renders the list of keyboard controls on the screen."""
        
        controls = [
            "Keyboard Controls:",
            "-------------------",
            "[X]  - Exit",
            "[I/O] - Rotate up/down",
            "[J/K] - Rotate left/right",
            "[N/M] - Zoom in/out",
            "[W/S] - Move up/down",
            "[A/D] - Move left/right",
            "[E/Q] - Scale simulation up/down",
            "[1] - Toggle orbit trails",
            "[2] - Toggle body display",
            "[3] - Toggle short orbit mode",
            "[=/-] - Increase/Decrease orbit length",
            "[[]/]] - Adjust simulation speed",
            "[R/T] - Adjust planet size",
            "Press SPACE to pause/unpause simulation",
        ]

        glDisable(GL_LIGHTING)  # Disable lighting to make text visible
        start_y = 300  # Adjust vertical start position
        for i, line in enumerate(controls):
            self.glut_print(10, start_y - (i * 15), GLUT_BITMAP_9_BY_15, line, 1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LIGHTING)  # Re-enable lighting after rendering text



class Definition:
    def __init__(self):             #InitialiglEnable(GL_CULL_FACE)zation of graphics
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

    def reshape(self, width, height):             #Manipulate with the window
        self.displayRatio = 1 * width / height
        self.windowWidth = width
        self.windowHeight = height
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(VIEW_ANGLE, self.displayRatio, WORLD_NEAR, WORLD_FAR)
        glViewport(0, 0, self.windowWidth, self.windowHeight)



def random_system(n_bodies):
    """Generates a purely random planetary system with N bodies."""
    system = Asystem(0)  # Start empty
    position = 5  # Define a reasonable spread
    velocity = 1  # Give some initial movement

    for i in range(n_bodies):
        mass_radius = uniform(1, 2e12)
        system.system.append(Body(i, 2452170.375,
                                  uniform(-position, position),
                                  uniform(-position, position),
                                  uniform(-position, position),
                                  uniform(-velocity, velocity),
                                  uniform(-velocity, velocity),
                                  uniform(-velocity, velocity),
                                  mass_radius,
                                  mass_radius / 1e12,
                                  uniform(0, 255), uniform(0, 255), uniform(0, 255), 0))
    return system

def random_system_with_star(n_bodies):
    """Generates a random planetary system with a central star."""
    system = Asystem(0)  # Start with an empty system
    # Create central star (ID 0)
    system.system.append(Body(0, 2452170.375, 0, 0, 0, 0, 0, 0, 1e20, 3, 253, 184, 19, 0))
    position = 5  # Defines the range of initial positions
    velocity = 1  # Defines the range of initial velocities
    for i in range(1, n_bodies):  # Start from 1 to avoid overwriting the sun
        mass_radius = uniform(1, 2e12)
        system.system.append(Body(i, 2452170.375,
                                  uniform(-position, position),
                                  uniform(-position, position),
                                  uniform(-position, position),
                                  uniform(-velocity, velocity),
                                  uniform(-velocity, velocity),
                                  uniform(-velocity, velocity),
                                  mass_radius,
                                  mass_radius / 1e12,
                                  uniform(0, 255), uniform(0, 255), uniform(0, 255), 0))
    return system

def main():
    """Handles command-line arguments and runs the correct simulation mode."""
    # Open file for writing simulation output
    output_filename = str(datetime.datetime.now()) + ".csv"
    global write_file
    write_file = open(output_filename, 'w')
    write_file.write('ident,             JDTDB,                      X,                      Y,                      Z,              VX (km/s),              VY (km/s),              VZ (km/s),             mass (kg),          radius (km),  color1,   color2,    color3,\n')
    
    # Initialize OpenGL
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    
    # glutInitWindowPosition(POSITION_X, POSITION_Y)   # Reverse the commenting on this paragraph to change between manual and automatic window positioning
    screen_width = glutGet(GLUT_SCREEN_WIDTH)
    screen_height = glutGet(GLUT_SCREEN_HEIGHT)
    pos_x = (screen_width - WIDTH) // 2  # Center horizontally
    pos_y = (screen_height - HEIGHT) // 2  # Center vertically
    glutInitWindowPosition(pos_x, pos_y)
    
    glutCreateWindow("N-Body")
    
    glGenTextures(1)
    
    # Initialize planetary system based on selected mode
    global planet_system
    if system_mode == "random":
        planet_system = random_system(num_bodies)  # Generate a purely random system
        print(f"Running in RANDOM mode with {num_bodies} bodies using 'configure_random.ini'.")
    elif system_mode == "random-star":
        planet_system = random_system_with_star(num_bodies)  # Generate random system with a central star
        print(f"Running in RANDOM-STAR mode with {num_bodies} bodies using 'configure_random.ini'.")
    else:
        planet_system = Asystem(SOLAR_SYSTEM_FILE)  # Load solar system data
        print("Running in SOLAR SYSTEM mode using 'configure.ini'.")
    
    # Initialize OpenGL definitions
    global init
    init = Definition()
    
    # Set display and animation functions
    if init.display:
        glutDisplayFunc(planet_system.display)
    glutIdleFunc(planet_system.animate)
    
    # Start the OpenGL main loop
    glutMainLoop()
    
    # Close output file
    write_file.close()
    print(f"Simulation data saved to {output_filename}")

if __name__ == "__main__":
    main()
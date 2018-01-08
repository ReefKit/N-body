import pandas as pd
import re
import random
import math

body = {'ident':0,
        'x':1,
        'y':2,
        'z':3,
        'Vx':4,
        'Vy':5,
        'Vz':6,
        'mass':7,
        'Vx_new':8,
        'Vy_new':9,
        'Vz_new':10, }

'''
file = 'N-body.csv'

df = pd.read_csv(file) #reads file

fb = re.search("\n",repr(df)) #searches for first break
hn = fb.start() #obtains last string index of heading
heading = repr(df)[:hn].split()

vals = repr(df).split()

count = 11
global bodies
bodies = []
no_body = int(len(vals) / 12)
one_body = []
while count < len(vals):
    count+=1
    one_body.append(vals[count - 1])
    if (count + 1) % 12 == 0:
        bodies.append(one_body)
        one_body = []

print(bodies)
print(bodies[2][body['x']])
'''


'''
Class holds attributes of a single body
'''

class Body(object):
    global_ident = 0
    def __init__(self, ident=None, x=None, y=None,z=None,Vx=None,Vy=None,Vz=None,mass=None):
        if ident == None:
            self.ident = Body.global_ident
            Body.global_ident += 1
        else:
            self.ident = ident
        if x == None:
            self.x = random.random()
        else:
            self.x = x
        if y == None:
            self.y = random.random()
        else:
            self.y = y
        if z == None:
            self.z = random.random()
        else:
            self.z = z
        if Vx == None:
            self.Vx = random.random()
        else:
            self.Vx = Vx
        if Vy == None:
            self.Vy = random.random()
        else:
            self.Vy = Vy
        if Vz == None:
            self.Vz = random.random()
        else:
            self.Vz = Vz
        self.Vx_new = 0
        self.Vy_new = 0
        self.Vz_new = 0
        if mass == None:
            self.mass = random.random()
        else:
            self.mass = mass
    def print(self):
        print("ident: " + str(self.ident)
              + ", x = " + str(self.x)
              + ", y = " + str(self.y)
              + ", z = " + str(self.z)
              + ", Vx = " + str(self.Vx)
              + ", Vy = " + str(self.Vy)
              + ", Vz = " + str(self.Vz)
              + ", mass = " + str(self.mass)
              + ", Vx_new = " + str(self.Vx_new)
              + ", Vy_new = " + str(self.Vy_new)
              + ", Vz_new = " + str(self.Vz_new))
    def force_cal(self, other_body, grav_cons):
        dx = other_body.x - self.x
        dy = other_body.y - self.y
        dz = other_body.z - self.z
        distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        force = grav_cons * self.mass * other_body.mass / (distance ** 2)
        angleBAM = math.asin(dz/distance)
        angleMAN = math.atan(dy/dx)
        AM = force * math.cos(angleBAM)
        Fx = AM * math.cos(angleMAN)
        Fy = AM * math.sin(angleMAN)
        Fz = force * math.sin(angleBAM)
        return (Fx, Fy, Fz)
    def velocity_cal(self, fx, fy, fz, time_int):
        Vx_new = self.Vx + (fx * time_int / self.mass)
        Vy_new = self.Vy + (fy * time_int / self.mass)
        Vz_new = self.Vz + (fz * time_int / self.mass)
        return (Vx_new, Vy_new, Vz_new)

'''
Class holds bodies
'''

class Asystem:
    def __init__(self,n_bodies=10):
        self.n_bodies = n_bodies
        self.system = []
        for i in range(self.n_bodies):
            self.system.append(Body())
    def __init__(self,file_name):
        self.system = self.read_from_file(file_name)
    def print(self):
        for body in self.system:
            body.print()
    def read_from_file(self,file_name):
        bodies = []
        for line in open(file_name):
            fields = line.split(",")
            if fields[1] != 'x':
                body = Body(str(fields[0]),
                            float(fields[1]),
                            float(fields[2]),
                            float(fields[3]),
                            float(fields[4]),
                            float(fields[5]),
                            float(fields[6]),
                            float(fields[7]))
                bodies.append(body)
        return bodies
    def write_to_file(self,file_name):
        data = 'ident,x,y,z,Vx,Vy,Vx,mass\n'
        for body in self.system:
            body_data = (body.ident + ","
                         + str(body.x) + ","
                         + str(body.y) + ","
                         + str(body.z) + ","
                         + str(body.Vx) + ","
                         + str(body.Vy) + ","
                         + str(body.Vz) + ","
                         + str(body.mass) + "\n")
            data += body_data
        file = open(file_name,'w')
        file.write(data)
        file.close()
    def simulate(self, grav_cons, time_int, total_time):
        time = 0
        while time < total_time:
            for body in self.system:
                for other_body in self.system:
                    None

if __name__ == "__main__":
    solar_system = Asystem(file_name='N-body.csv')
    solar_system.print()
    solar_system.write_to_file('test_output.csv')
    test_system = Asystem(file_name='test_output.csv')
    test_system.print()
    '''
    solar_system = Asystem()
    solar_system.print()
    '''

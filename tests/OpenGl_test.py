from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

window = 0                                             # glut window number
length, width, height = 600, 500, 400                               # window size

def draw():                                            # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d(width, height, length)                           # set mode to 2d

    glColor3f(.5, 1.0, 1.0)                           # set color to blue
    draw_rect(10, 10, 200, 100)                        # rect at (10, 10) with width 200, height 100

    glutSwapBuffers()                                  # important for double buffering

def refresh2d(width, height, length):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 0.0, length)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def main():     # initialization
    glutInit(sys.argv)                                             # initialize glut
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)                      # set window size
    glutInitWindowPosition(0, 0)                           # set window position
    window = glutCreateWindow("noobtuts.com")              # create window with title
    glutDisplayFunc(draw)                                  # set draw function callback
    glutIdleFunc(draw)                                     # draw all the time
    glutMainLoop()                                         # start everything

def draw_rect(x, y, width, height):
    gluLookAt()

if __name__ == '__main__':
    main()

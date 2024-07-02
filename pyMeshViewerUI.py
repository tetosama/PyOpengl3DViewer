"""
This file implements the UI (Mainly buttons for now)
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from UI_Button import *

class PyMeshViewerUI:
    width = 0
    height = 0


    def __init__(self, width, height):
        PyMeshViewerUI.width = width
        PyMeshViewerUI.height = height

        self.mouse_callbacks = []
        self.buttons = []
        self.buttons.append(UI_SwitchButton_VertexSelect(50, 50, 100, 30, "vertex"))
        self.buttons.append(UI_SwitchButton_TriangleSelect(50, 100, 100, 30, "triangle"))

        for i in range(len(self.buttons)):
            self.mouse_callbacks.append(self.buttons[i].mouse_callback)
            

    def mouse_callback(self, button, state, x, y):
        for i in self.mouse_callbacks:
            i(button, state, x, y)


    def render(self):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, PyMeshViewerUI.width, 0, PyMeshViewerUI.height)  # Set the orthographic view to match the window size
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        for i in range(len(self.buttons)):
            self.buttons[i].render()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)

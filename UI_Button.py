"""
This file contains the UI_Button class, which is a base class for all buttons in the UI.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from instances import Instances

class UI_Button:
    def __init__(self, x, y, width, height, text=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = (0.5, 0.5, 0.5)
        
    def on_click(self):
        pass

    def mouse_callback(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Check if the click coordinates are within the button's bounding box
            if self.x <= x and x <= self.x + self.width and self.y <= y and y <= self.y + self.height:
                self.on_click()
    
    def render(self):
        # Draw the button rectangle
        glColor3f(*self.color)  # Gray color
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        self.render_text()

    def render_text(self):
        position = (self.x + self.width / 4, self.y + self.height / 2)
        glColor3f(1,1,1)
        glRasterPos2f(*position)
        for char in self.text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))


class UI_SwitchButton(UI_Button):
    def __init__(self, x, y, width, height, text=""):
        super().__init__(x,y,width, height, text)
        self.isEnabled = False

    def on_click(self):
        self.isEnabled = not self.isEnabled

    def render(self):
        if self.isEnabled:
            self.color = (0.61, 0.97, 0.51)  # Gray color
        else:
            self.color = (0.5, 0.5, 0.5)
        super().render()

class UI_SwitchButton_VertexSelect(UI_SwitchButton):
    def __init__(self, x, y, width, height, text=""):
        super().__init__(x,y,width, height, text)
    
    def on_click(self):
        self.isEnabled = not self.isEnabled
        if self.isEnabled:
            Instances.particle_system_instance.select_particle_enabled = True
        else:
            Instances.particle_system_instance.select_particle_enabled = False
    
    def render(self):
        self.isEnabled = Instances.particle_system_instance.select_particle_enabled
        super().render()

class UI_SwitchButton_TriangleSelect(UI_SwitchButton):
    def __init__(self, x, y, width, height, text=""):
        super().__init__(x,y,width, height, text)
    
    def on_click(self):
        self.isEnabled = not self.isEnabled
        if self.isEnabled:
            Instances.particle_system_instance.select_triangle_enabled = True
        else:
            Instances.particle_system_instance.select_triangle_enabled = False
    
    def render(self):
        self.isEnabled = Instances.particle_system_instance.select_triangle_enabled
        super().render()
        
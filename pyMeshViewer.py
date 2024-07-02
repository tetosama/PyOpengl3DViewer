"""
    This is the main file for the PyMeshViewer application. It initializes the OpenGL window and sets up the rendering loop.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from camera import Camera
from inputHandler import InputHandler
from OBJLoader import OBJLoader
from particleSystem import ParticleSystem
from UI_Button import UI_Button
from pyMeshViewerUI import PyMeshViewerUI
from pyMeshViewerUtils import *
from instances import *
import threading
from terminalManager import *

# Window dimensions
width, height = 800, 600
PyMeshViewerUtils.width = width
PyMeshViewerUtils.height = height

Instances.camera_instance = Camera()
Instances.input_handler_instance = InputHandler(Instances.camera_instance, width, height)
model = OBJLoader('cube.obj')
Instances.debuggerUI_instance = PyMeshViewerUI(width, height)

server_up_event = threading.Event()


def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Setup perspective projection
    gluPerspective(45.0, float(width)/float(height), 0.1, 50.0)
    Instances.camera_instance.projection = glGetFloatv(GL_PROJECTION_MATRIX)

    # Calculate view target based on camera's orientation
    u, v, w = Instances.camera_instance.compute_direction_vectors()
    target = Instances.camera_instance.camera_pos + w

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Set the view matrix using gluLookAt
    gluLookAt(Instances.camera_instance.camera_pos[0], Instances.camera_instance.camera_pos[1], Instances.camera_instance.camera_pos[2], 
              target[0], target[1], target[2],  # Look at the calculated target
              0, 1, 0)  # Up vector
    Instances.camera_instance.modelView = glGetFloatv(GL_MODELVIEW_MATRIX)
    Instances.camera_instance.viewPort = glGetIntegerv(GL_VIEWPORT)

    # render the model
    Instances.particle_system_instance.render()
    Instances.debuggerUI_instance.render()

    glutSwapBuffers()

def start_command_daemon():
    Instances.terminalManager_instance = TerminalManager()
    # Start the asyncio loop in a separate thread
    loop_thread = threading.Thread(target=Instances.terminalManager_instance.start_async_loop)
    loop_thread.start()

def main():
    global width, height
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow("3D Scene")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(render_scene)
    glutIdleFunc(render_scene)
    glutKeyboardFunc(Instances.input_handler_instance.keyboard)
    glutMouseFunc(Instances.input_handler_instance.mouse)
    Instances.input_handler_instance.mouseCallbacks.append(Instances.debuggerUI_instance.mouse_callback)
    glutMotionFunc(Instances.input_handler_instance.mouse_motion)

    command_daemon_thread = threading.Thread(target=start_command_daemon)
    command_daemon_thread.start()

    Instances.particle_system_instance.init_buffers()

    glutMainLoop()

main()
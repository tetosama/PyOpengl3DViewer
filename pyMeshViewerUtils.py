"""
This file contains utility functions for the PyMeshViewer class.
"""

from camera import *
from inputHandler import *
from vector3 import *
import numpy as np
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class PyMeshViewerUtils:
    def world_to_screen(point, modelView, projection, viewPort):
        # Convert the 3D point to a 4D homogeneous coordinate
        homogeneous_point = [point[0], point[1], point[2], 1.0]
        
        # Transform the point to clip space
        # Since OpenGL use column major, we need to transpose the matrices
        clip_space_point = np.transpose(projection) @ (np.transpose(modelView) @ homogeneous_point)

        ndcSpacePos = np.array([clip_space_point[0]/clip_space_point[3], clip_space_point[1]/clip_space_point[3], clip_space_point[2]/clip_space_point[3]])

        screen_x = ((ndcSpacePos[0] + 1.0) / 2.0) * viewPort[2] + viewPort[0]
        screen_y = ((ndcSpacePos[1] + 1.0) / 2.0) * viewPort[3] + viewPort[1]

        return (screen_x, screen_y)
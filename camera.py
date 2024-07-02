"""
This file contains the Camera class, which is used to represent the camera in the 3D world.
"""

from vector3 import Vector3
import math

class Camera:
    def __init__(self):
        self.camera_pos = Vector3(0.0, 0.0, 5.0)
        self.camera_angle = [0.0, 0.0]  # [pitch, yaw]
        self.camera_speed = 0.1
        self.projection = None
        self.modelView = None
        self.viewPort = None
        
    def compute_direction_vectors(self):
        # Calculate the w (forward) vector from pitch and yaw
        w = Vector3(
            -math.sin(math.radians(self.camera_angle[1])) * math.cos(math.radians(self.camera_angle[0])),
            -math.sin(math.radians(self.camera_angle[0])),
            -math.cos(math.radians(self.camera_angle[1])) * math.cos(math.radians(self.camera_angle[0]))
        )

        w = w.normalize()
        world_up = Vector3(0.0, 1.0, 0.0)
        u = world_up.cross(w)
        u = u.normalize()
        v = w.cross(u)

        return u, v, w
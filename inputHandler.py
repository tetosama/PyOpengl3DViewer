"""
This file contains the InputHandler class, which is responsible for handling user input.
"""

from camera import Camera
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from particleSystem import *
import numpy as np
import json
from instances import Instances
import threading
import vector3

class InputHandler:
    def __init__(self, camera, width, height):
        self.window_width = width
        self.window_height = height
        self.camera = camera
        self.mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0, 0
        self.mouseCallbacks = []
        self.mouseCallbacksWithRayIntersection = []
        
    def keyboard(self, key, x, y):
        u, v, w = self.camera.compute_direction_vectors()

        if key == b'w':
            self.camera.camera_pos += w * self.camera.camera_speed
        elif key == b's':
            self.camera.camera_pos -= w * self.camera.camera_speed
        elif key == b'a':
            self.camera.camera_pos += u * self.camera.camera_speed
        elif key == b'd':
            self.camera.camera_pos -= u * self.camera.camera_speed
        elif key == b'\x1b':  # ESC key
            sys.exit()

        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        # convert y value
        converted_y = self.window_height - y

        if button == GLUT_RIGHT_BUTTON:
            if state == GLUT_DOWN:
                self.mouse_dragging = True
                self.last_mouse_x, self.last_mouse_y = x, y
            else:
                self.mouse_dragging = False
        
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_UP:
                (origin, direction) = self.get_ray_from_mouse(x, y)
                for callback in self.mouseCallbacksWithRayIntersection:
                    callback(button, state, x, converted_y, Vector3(origin[0], origin[1], origin[2]), Vector3(direction[0], direction[1], direction[2]))


        for i in range(len(self.mouseCallbacks)):
            self.mouseCallbacks[i](button, state, x, converted_y)

    def mouse_motion(self, x, y):
        if self.mouse_dragging:
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            self.camera.camera_angle[1] -= dx * 0.5  # yaw
            self.camera.camera_angle[0] = max(min(self.camera.camera_angle[0] + dy * 0.5, 89), -89)  # pitch clamped

            self.last_mouse_x, self.last_mouse_y = x, y
            glutPostRedisplay()

    def get_ray_from_mouse(self, x, y):
        modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        y = viewport[3] - y
        
        winZ_near = 0.0  # Near plane
        winZ_far = 1.0   # Far plane
        
        ray_near_world = gluUnProject(x, y, winZ_near, modelview_matrix, projection_matrix, viewport)
        ray_far_world = gluUnProject(x, y, winZ_far, modelview_matrix, projection_matrix, viewport)
        
        ray_near_world = np.array(ray_near_world, dtype=np.float32)
        ray_far_world = np.array(ray_far_world, dtype=np.float32)
        
        direction = ray_far_world - ray_near_world
        direction = direction / np.linalg.norm(direction)
        
        return self.camera.camera_pos, direction
    
    def command(self, str):
        cmd = str.split(" ")
        
        # Highlight commands take in 3 arguments
        # e.g.: highlight vertex 0
        if cmd[0] == "highlight" or cmd[0] == "hl":
            if len(cmd) < 3:
                Instances.terminalManager_instance.tprint("Highlight commands take in 3 arguments.")
                return

            index = int(cmd[2])

            if cmd[1] == "vertex" or cmd[1] == "v":
                Instances.particle_system_instance.highlight_vertex(index)
            elif cmd[1] == "triangle" or cmd[1] == "t":
                Instances.particle_system_instance.highlight_triangle(index)
            else:
                Instances.terminalManager_instance.tprint("Invalid highlight type.")
                return
            
            glutPostRedisplay()

        if cmd[0] == "loadAnimation" or cmd[0] == "la":
            if len(cmd) < 2:
                Instances.terminalManager_instance.tprint("Load animation commands take in 1 arguments.")
                return

            path = cmd[1]
            data = self.decode_animation_data(path)
            # Get first set of vertices
            Instances.particle_system_instance.load_animation(data)
            glutPostRedisplay()
        
        if cmd[0] == "animation":
            if len(cmd) < 2:
                Instances.terminalManager_instance.tprint("No arguments provided!")
                return

            if cmd[1] == "animate":
                if len(cmd) != 5:
                    Instances.terminalManager_instance.tprint("Invalid number of arguments!")
                    return
            
                start_index = int(cmd[2])
                end_index = int(cmd[3])
                dt = float(cmd[4])
                threading.Thread(target=Instances.particle_system_instance.animation_manager.animate, args=[start_index, end_index, dt]).start()
            
            elif cmd[1] == "pause":
                Instances.particle_system_instance.animation_manager.pause()

            elif cmd[1] == "resume":
                Instances.particle_system_instance.animation_manager.resume()

            elif cmd[1] == "track":
                if len(cmd) != 3:
                    Instances.terminalManager_instance.tprint("Invalid number of arguments!")
                    return

                index = int(cmd[2])
                Instances.particle_system_instance.animation_manager.track(index)
            
            elif cmd[1] == "stop":
                Instances.particle_system_instance.animation_manager.stop()

            elif cmd[1] == "mark":
                if len(cmd) != 4:
                    Instances.terminalManager_instance.tprint("Invalid number of arguments!")
                    return

                index = int(cmd[2])
                name = cmd[3]
                Instances.particle_system_instance.animation_manager.mark(index, name)
            
            elif cmd[1] == "goto":
                if len(cmd) != 3:
                    Instances.terminalManager_instance.tprint("Invalid number of arguments!")
                    return

                name = cmd[2]
                Instances.particle_system_instance.animation_manager.goto(name)

    
    def redisplay(self):
        glutPostRedisplay()

    def decode_animation_data(self, file_path):
        """
        Reads a JSON-encoded file and decodes it into Python variables.

        Parameters:
        file_path (str): The path to the JSON file.

        Returns:
        dict: A dictionary containing the decoded JSON data.
        """
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            return data

        except json.JSONDecodeError as e:
            print(f"An error occurred while decoding JSON: {e}")
        except FileNotFoundError:
            print(f"The file {file_path} was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

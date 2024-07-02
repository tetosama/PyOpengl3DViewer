"""
    This file contains the ParticleSystem class, which is responsible for rendering the particles and triangles of the mesh. 
    It also contains the Particle and Triangle classes, which are used to represent the particles and triangles of the mesh, respectively.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from vector3 import Vector3
from pyMeshViewerUtils import *
from instances import *
import time
from animationManager import AnimationManager

class ParticleSystem:
    def __init__(self, vertices, triangleIndices, indexOffset = -1):
        self.animation_manager = None

        self.particles = []
        self.triangles = []
        self.lines = []
        for i in range(len(vertices)):
            self.particles.append(Particle(Vector3(vertices[i][0], vertices[i][1], vertices[i][2]), self))
        
        for i in range(0, len(triangleIndices), 3):
                self.triangles.append(Triangle(triangleIndices[i + 0] + indexOffset, triangleIndices[i + 1] + indexOffset, triangleIndices[i + 2] + indexOffset, self))

        self.select_particle_enabled = False
        self.select_triangle_enabled = False
        self.selected_element_index = -1

        self.vbo = None
        self.ebo = None
        self.need_to_refresh_buffers = False

        self.show_highlights_only = False

        Instances.input_handler_instance.mouseCallbacksWithRayIntersection.append(self.on_mouse_click)

    # Initialize the VBOs and EBOs for drawing
    def init_buffers(self):
        np_particles = self.particles_to_np_array()
        np_triangles = self.triangles_to_np_array()

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, np_particles.nbytes, np_particles.tobytes(), GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np_triangles.nbytes, np_triangles.tobytes(), GL_STATIC_DRAW)

  
    # Callback function for mouse click events
    def on_mouse_click(self, button, state, x, y, origin, direction):
        if self.select_triangle_enabled:
            self.select_triangle(origin, direction)        

        if self.select_particle_enabled:
            self.select_particle(x, y)
        
    # Select the particle that is closest to the mouse click
    def select_particle(self, x, y):
        closest_hit_vertex = -1
        smallest_distance = float("inf")
        for i in range(len(self.particles)):
            p = self.particles[i]
            onscreen_x, onscreen_y = PyMeshViewerUtils.world_to_screen(p.position.np(), Instances.camera_instance.modelView, Instances.camera_instance.projection, Instances.camera_instance.viewPort)
            distance = math.sqrt((onscreen_x - x) ** 2 + (onscreen_y - y) ** 2)
            if distance < smallest_distance:
                closest_hit_vertex = i
                smallest_distance = distance

        if smallest_distance < 5:
            p = self.particles[closest_hit_vertex]
            Instances.terminalManager_instance.tprint("Hit vertex index: {}, position: ({}, {}, {})".format(closest_hit_vertex, p.position.x, p.position.y, p.position.z))
            self.selected_element_index = closest_hit_vertex
    
    # Select the triangle that is hit by the ray
    def select_triangle(self, origin, direction):
        smallest_distance = float("inf")
        closest_hit_triangle = -1
        for i in range(len(self.triangles)):
            t = self.triangles[i]
            distance = t.intersect_with_ray(origin, direction)
            if distance is not None and distance < smallest_distance:
                closest_hit_triangle = i
                smallest_distance = distance
        Instances.terminalManager_instance.tprint("Hit triangle index: {}".format(closest_hit_triangle))
        hitTriangle = self.triangles[closest_hit_triangle]
        self.selected_element_index = closest_hit_triangle
        p0 = self.particles[hitTriangle.index0].position
        p1 = self.particles[hitTriangle.index1].position
        p2 = self.particles[hitTriangle.index2].position
        Instances.terminalManager_instance.tprint("Triangle Vertex Indices: {}, {}, {}".format(hitTriangle.index0, hitTriangle.index1, hitTriangle.index2))
        Instances.terminalManager_instance.tprint("Triangle Vertices: {}, {}, {}".format(p0, p1, p2))


    """
    Load animation and create animation manager. Data is json data.
    """
    def load_animation(self, data):
        animation_vertices = []
        animation_triangles = []
        animation_frame_types = []
        for frame in data['frames']:
            frame_vertices = []
            for vertex in frame['points']:
                frame_vertices.append([vertex['X'], vertex['Y'], vertex['Z']])
            animation_vertices.append(frame_vertices)
            animation_frame_types.append(frame['type'])
        for t in data['triangle_indices']:
            animation_triangles.append(t['A'])
            animation_triangles.append(t['B'])
            animation_triangles.append(t['C'])
        
        self.particles = []
        self.triangles = []

        for i in range(len(animation_vertices[0])):
            self.particles.append(Particle(Vector3(animation_vertices[0][i][0], animation_vertices[0][i][1], animation_vertices[0][i][2]), self))
        
        for i in range(0, len(animation_triangles), 3):
            self.triangles.append(Triangle(animation_triangles[i + 0], animation_triangles[i + 1], animation_triangles[i + 2], self))
        
        self.vbo = None
        self.ebo = None

        self.animation_manager = AnimationManager(self, animation_vertices, animation_frame_types)

        glutPostRedisplay()

    # Update the vertices of the particle system
    def update_vertices(self, vertices):
        self.particles = []
        for i in range(len(vertices)):
            self.particles.append(Particle(Vector3(vertices[i][0], vertices[i][1], vertices[i][2]), self))

        self.need_to_refresh_buffers = True
        glutPostRedisplay()

    # Convert particles to numpy array
    def particles_to_np_array(self):
        result = np.array([], dtype=np.float32)
        for p in self.particles:
            result = np.append(result, p.position.np())
        return result
    
    # Convert triangles to numpy array
    def triangles_to_np_array(self):
        result = np.array([], dtype=np.uint32)
        for t in self.triangles:
            result = np.append(result, np.array([t.index0], dtype=np.uint32))
            result = np.append(result, np.array([t.index1], dtype=np.uint32))
            result = np.append(result, np.array([t.index2], dtype=np.uint32))
        return result

    def render(self):
        if self.vbo is None or self.ebo is None:
            self.init_buffers()
        elif self.need_to_refresh_buffers:
            new_np_particles = self.particles_to_np_array()
            new_np_triangles = self.triangles_to_np_array()

            # Bind the VBO
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

            # Update the VBO with new data
            glBufferSubData(GL_ARRAY_BUFFER, 0, new_np_particles.nbytes, new_np_particles.tobytes())

            # Bind the EBO
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

            # Update the EBO with new data
            glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, new_np_triangles.nbytes, new_np_triangles.tobytes())

            self.need_to_refresh_buffers = False


        if not self.show_highlights_only:

            # Set up VBOs and EBOs for drawing
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            
            # Enable the vertex attribute array (assuming 0 is for vertices)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.triangles_to_np_array().itemsize * 3, ctypes.c_void_p(0))
            
            # Draw filled triangles
            glColor3f(0.99, 0.99, 0.99)
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(1.0, 1.0)
            glDrawElements(GL_TRIANGLES, len(self.triangles) * 3, GL_UNSIGNED_INT, None)
            glDisable(GL_POLYGON_OFFSET_FILL)
            
            # Draw wireframe/edges
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glColor3f(0, 0, 0)
            glLineWidth(1.5)
            glDrawElements(GL_TRIANGLES, len(self.triangles) * 3, GL_UNSIGNED_INT, None)
            
            # Reset to fill mode for other renderings
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glColor3f(0.0, 0.0, 0.0)  # Set line color to white
            glBegin(GL_LINES)  # Begin drawing lines
            for i in self.lines:
                glVertex3f(i.x, i.y, i.z)
            glEnd()
            # Revert settings (optional, depending on your render loop)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glPolygonOffset(1.0, 1.0)
            glPointSize(5.0)
            glColor3f(0.11, 0.99, 0.11)
            glDrawArrays(GL_POINTS, 0, len(self.particles))

        # Disable depth testing temporarily to ensure red particle is always on top
        glDisable(GL_DEPTH_TEST)

        if self.select_triangle_enabled:
            triangle = self.triangles[self.selected_element_index]
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(0.0, 0.0)  # Adjust these values as needed
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBegin(GL_TRIANGLES)
            glColor3f(0.99, 0.11, 0.11)
                
            v0 = self.particles[triangle.index0].position
            v1 = self.particles[triangle.index1].position
            v2 = self.particles[triangle.index2].position
            glVertex3fv([v0.x, v0.y, v0.z])
            glVertex3fv([v1.x, v1.y, v1.z])
            glVertex3fv([v2.x, v2.y, v2.z])
            glEnd()
            glDisable(GL_POLYGON_OFFSET_FILL)

        glColor3f(0.99, 0.99, 0.99)
        # Render particles
        """
        glPointSize(5.0)
        glBegin(GL_POINTS)
        for i in range(len(self.particles)):
            p = self.particles[i]
            if self.select_particle_enabled and i == self.selected_element_index:
                glColor3f(0.99, 0.11, 0.11)
            else:
                glColor3f(0.11, 0.99, 0.11)
            glVertex3f(p.position.x, p.position.y, p.position.z)
        glEnd()
        glColor3f(1, 1, 1)  # Set color back to white
        """
        # Render the selected particle in red
        if self.select_particle_enabled:
            glPolygonOffset(0.0, 0.0)
            glPointSize(6.0)
            particle = self.particles[self.selected_element_index]
            glBegin(GL_POINTS)
            glColor3f(0.99, 0.11, 0.11)    
            v0 = particle.position
            glVertex3fv([v0.x, v0.y, v0.z])
            glEnd()

        # Re-enable depth testing if required by other rendering steps
        glEnable(GL_DEPTH_TEST)
            
    # Highlight the vertex at the given index
    def highlight_vertex(self, index):
        self.select_particle_enabled = True
        self.select_triangle_enabled = False
        self.selected_element_index = index

    # Highlight the triangle at the given index
    def highlight_triangle(self, index):
        self.select_particle_enabled = False
        self.select_triangle_enabled = True
        self.selected_element_index = index

class Particle:
    # position is a Vector3
    def __init__(self, position, particle_system):
        self.position = position
        self.particle_system = particle_system

class Triangle:
    # v0, v1, v2 are integers representing the index of the vertex
    def __init__(self, index0, index1, index2, particle_system):
        self.index0 = index0
        self.index1 = index1
        self.index2 = index2
        self.particle_system = particle_system
        
    def get_vertices(self):
        v0 = self.particle_system.particles[self.index0].position
        v1 = self.particle_system.particles[self.index1].position
        v2 = self.particle_system.particles[self.index2].position
        
        return v0, v1, v2
        
    def is_illegal(self):
        (v0, v1, v2) = self.get_vertices()
        return np.array_equal(v0, v1) or np.array_equal(v1, v2) or np.array_equal(v2, v0)
        
    def calculate_normal(self):
        if self.is_illegal():
            return np.array([0, 0, 0])
        
        (v0, v1, v2) = self.get_vertices()
        
        e1 = v1 - v0
        e2 = v2 - v0
        
        return e1.cross(e2)

    # Möller–Trumbore Intersection Algorithm
    def intersect_with_ray(self, ray_origin, ray_direction):
        EPSILON = 0.00000001

        v0, v1, v2 = self.get_vertices()

        e1 = v1 - v0
        e2 = v2 - v0

        h = ray_direction.cross(e2)
        a = e1.dot(h)

        if a > -EPSILON and a < EPSILON:
            return None

        f = 1.0/a
        s = ray_origin - v0
        u = f * (s.dot(h))

        if u < 0.0 or u > 1.0:
            return None

        q = s.cross(e1)
        v = f * ray_direction.dot(q)

        if v < 0.0 or u + v > 1.0:
            return None

        t = f * e2.dot(q)

        if t > EPSILON:
            return t

        return None
    
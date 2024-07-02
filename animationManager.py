"""
This file contains the AnimationManager class, which is responsible for managing the animation of the particle system.
"""

from instances import Instances
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time

class AnimationManager:
    def __init__(self, particle_system, animation_frames, animation_frame_types):
        self.animation_index = -1
        self.animation_frames = animation_frames
        self.particle_system = particle_system
        self.animation_frame_types = animation_frame_types
        self.animating = False
        self.paused = False
        self.tracking_vertex = -1
        self.stop_animation = False
        self.marks = {}

    def tprint(self, s):
        Instances.terminalManager_instance.tprint("[Animation] " + s)

    # Animate the particle system from start_index to end_index with a delay of dt
    def animate(self, start_index, end_index, dt):
        self.animating = True

        if start_index > end_index:
            return
        
        if start_index > len(self.animation_frames) or end_index > len(self.animation_frames):
            return

        for i in range(start_index, end_index):
            while self.paused:
                time.sleep(dt)
            if self.stop_animation:
                self.stop_animation = False
                self.animating = False
                return
            

            self.animation_index = i

            prev_position = None
            if self.tracking_vertex != -1:
                # Get change of position
                prev_position = self.particle_system.particles[self.tracking_vertex].position

            self.particle_system.update_vertices(self.animation_frames[i])
            self.particle_system.frame_type = self.animation_frame_types[i]

            self.tprint("Animating frame {}, type {}".format(i, self.animation_frame_types[i]))
            if self.tracking_vertex != -1:
                self.particle_system.select_particle_enabled = True
                self.particle_system.select_triangle_enabled = False
                self.particle_system.selected_element_index = self.tracking_vertex
                curr_position = self.particle_system.particles[self.tracking_vertex].position
                self.tprint("Tracking Vertex Position: {}, Change of Position: {}\n".format(curr_position, curr_position - prev_position))
            
            time.sleep(dt)
        self.animating = False

    # Pause the animation
    def pause(self):
        self.paused = True
        self.tprint("Paused animation.")

    # Resume the animation
    def resume(self):
        self.paused = False
        self.tprint("Resumed animation.")

    # Track a specific vertex
    def track(self, index):
        self.tracking_vertex = index
        self.tprint("Tracking vertex {}.".format(index))

    # Stop the animation
    def stop(self):
        self.stop_animation = True
        self.tprint("Stopped animation.")

    # Go to a specific frame
    def goto(self, name):
        index = -1
        if name.isnumeric():
            index = int(name)
        elif self.marks[name] != None:
            index = self.marks[name]
        else:
            self.tprint("No such mark!")
            return

        self.stop()
        self.animation_index = index
        self.particle_system.update_vertices(self.animation_frames[index])
        self.particle_system.frame_type = self.animation_frame_types[index]
        self.tprint("Animating frame {}, type {}".format(index, self.animation_frame_types[index]))
        if self.tracking_vertex != -1:
                self.particle_system.select_particle_enabled = True
                self.particle_system.select_triangle_enabled = False
                self.particle_system.selected_element_index = self.tracking_vertex
                curr_position = self.particle_system.particles[self.tracking_vertex].position
                self.tprint("Tracking Vertex Position: {}\n".format(curr_position))

    # Mark a frame with a name
    def mark(self, index, name):
        self.marks[index] = name
        self.tprint("Marked frame {} as {}.".format(index, name))
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from instances import Instances
from particleSystem import ParticleSystem

class OBJLoader:
    def __init__(self, filename):
        vertices = []
        faces = []
        
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 0:
                    continue
                if parts[0] == 'v':
                    vertices.append(list(map(float, parts[1:4])))
                elif parts[0] == 'f':
                    faces.append(int(parts[1]))
                    faces.append(int(parts[2]))
                    faces.append(int(parts[3]))

        Instances.particle_system_instance = ParticleSystem(vertices, faces, indexOffset=-1)
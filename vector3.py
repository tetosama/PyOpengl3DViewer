"""
    This function implements basic 3D vector operations.
"""

import math
import numpy as np

class Vector3:
    def __init__(self, *args):
        if len(args) == 0:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
        elif len(args) == 1:
            if type(args[0]) is np.ndarray:
                self.x = args[0]
                self.y = args[0]
                self.z = args[0]
            else:
                print("Vector3: input is not a numpy array!")
                self.x = 0.0
                self.y = 0.0
                self.z = 0.0
        elif len(args) == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        else:
            print("Vector3: initializing with wrong number of arguments!")
        
    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            print("accessing null!")
            return None
    
    def __setitem__(self, item, value):
        if item == 0:
            self.x = value
        elif item == 1:
            self.y = value
        elif item == 2:
            self.z = value
        else:
            print("setting null!")
            return None
        
    def __add__(self, target):
        return Vector3(self.x + target.x, self.y + target.y, self.z + target.z)
    
    def __radd__(self, target):
        return Vector3(self.x + target.x, self.y + target.y, self.z + target.z)
    
    def __sub__(self, target):
        return Vector3(self.x - target.x, self.y - target.y, self.z - target.z)
    
    def __rsub__(self, target):
        return Vector3(target.x - self.x, target.y - self.y, target.z - self.z)
    
    def __mul__(self, target):
        return Vector3(self.x * target, self.y * target, self.z * target)
    
    def __rmul__(self, target):
        return Vector3(self.x * target, self.y * target, self.z * target)
    
    def __truediv__(self, target):
        if target == 0:
            print("Deviding by zero!")
            return Vector3(0.0, 0.0, 0.0)
        
        return Vector3(self.x * (1.0/target), self.y * (1.0/target), self.z * (1.0/target))
    
    def __rtruediv__(self, target):
        if target == 0:
            return Vector3(0.0, 0.0, 0.0)
        
        return Vector3(1/self.x, 1/self.y, 1/self.z)
    
    def __str__(self):
        return "({:.6f}, {:.6f}, {:.6f})".format(self.x, self.y, self.z)

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        return Vector3(self.x / self.magnitude(), self.y / self.magnitude(), self.z / self.magnitude())
    
    def cross(self, rhs):
        return Vector3(self.y * rhs.z - self.z * rhs.y, self.z * rhs.x - self.x * rhs.z, self.x * rhs.y - self.y * rhs.x)
    
    def dot(self, rhs):
        return self.x * rhs.x + self.y * rhs.y + self.z * rhs.z
    
    def np(self):
        return np.array([self.x, self.y, self.z], dtype=np.float32)

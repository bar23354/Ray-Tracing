import numpy as np
from intercept import Intercept

class Material:
    def __init__(self, diffuse = [1,1,1], spec = 1.0, ks = 0.0):
        self.diffuse = diffuse
        self.spec = spec
        self.ks = ks

class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material
        self.type = "None"

    def ray_intersect(self, ray_origin, ray_direction):
        return False
    
class Sphere(Shape):
    def __init__(self, center, radius, material):
        super().__init__(center, material)
        self.center = np.array(center)
        self.radius = radius
        self.type = "Sphere"

    def ray_intersect(self, ray_origin, ray_direction):
        ray_origin = np.array(ray_origin)
        ray_direction = np.array(ray_direction)
        
        L = self.center - ray_origin
        tca = np.dot(L, ray_direction)
        
        d = np.linalg.norm(L)**2 - tca**2
        
        if d > self.radius**2:
            return None
            
        thc = (self.radius**2 - d)**0.5
        t0 = tca - thc
        t1 = tca + thc
        
        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None
            
        point = ray_origin + ray_direction * t0
        normal = (point - self.center) / np.linalg.norm(point - self.center)
        
        return {
            'distance': t0,
            'point': point,
            'normal': normal,
            'material': self.material,
            'obj': self
        }
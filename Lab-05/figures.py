import numpy as np

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
        self.center = center
        self.radius = radius
        self.type = "Sphere"

    def ray_intersect(self, ray_origin, ray_direction):
        return None
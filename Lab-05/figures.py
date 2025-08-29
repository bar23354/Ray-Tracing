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
        L = np.subtract(self.center, ray_origin)
        tca = np.dot(L, ray_direction)
        d_squared = np.dot(L, L) - tca * tca
        
        if d_squared > self.radius ** 2:
            return None
            
        thc = np.sqrt(self.radius ** 2 - d_squared)
        t0 = tca - thc
        t1 = tca + thc
        
        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None
            
        hit_point = np.add(ray_origin, t0 * np.array(ray_direction))
        normal = np.subtract(hit_point, self.center)
        normal = normal / np.linalg.norm(normal)
        
        return {
            'distance': t0,
            'point': hit_point,
            'normal': normal,
            'material': self.material
        }
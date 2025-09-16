import numpy as np
from intercept import Intercept

class Material:
    def __init__(self, diffuse = [1,1,1], spec = 1.0, ks = 0.0, matType = "OPAQUE", ior = 1.0):
        self.diffuse = diffuse
        self.spec = spec
        self.ks = ks
        self.matType = matType
        self.ior = ior

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
        normal = (point - self.center)
        normal = normal / np.linalg.norm(normal)
        
        return {
            'distance': t0,
            'point': point,
            'normal': normal,
            'material': self.material,
            'obj': self
        }

class Plane(Shape):
    def __init__(self, position, normal, material):
        super().__init__(position, material)
        self.position = np.array(position)
        self.normal = np.array(normal) / np.linalg.norm(normal)
        self.type = "Plane"

    def ray_intersect(self, ray_origin, ray_direction):
        ray_origin = np.array(ray_origin)
        ray_direction = np.array(ray_direction)
        
        denom = np.dot(self.normal, ray_direction)
        if abs(denom) < 1e-6:
            return None
            
        t = np.dot(self.position - ray_origin, self.normal) / denom
        if t < 0:
            return None
            
        point = ray_origin + ray_direction * t
        
        return {
            'distance': t,
            'point': point,
            'normal': self.normal,
            'material': self.material,
            'obj': self
        }

class Disk(Shape):
    def __init__(self, position, normal, radius, material):
        super().__init__(position, material)
        self.position = np.array(position)
        self.normal = np.array(normal) / np.linalg.norm(normal)
        self.radius = radius
        self.type = "Disk"

    def ray_intersect(self, ray_origin, ray_direction):
        ray_origin = np.array(ray_origin)
        ray_direction = np.array(ray_direction)
        
        denom = np.dot(self.normal, ray_direction)
        if abs(denom) < 1e-6:
            return None
            
        t = np.dot(self.position - ray_origin, self.normal) / denom
        if t < 0:
            return None
            
        point = ray_origin + ray_direction * t
        distance_to_center = np.linalg.norm(point - self.position)
        
        if distance_to_center > self.radius:
            return None
            
        return {
            'distance': t,
            'point': point,
            'normal': self.normal,
            'material': self.material,
            'obj': self
        }

class Triangle(Shape):
    def __init__(self, v0, v1, v2, material):
        super().__init__(v0, material)
        self.v0 = np.array(v0)
        self.v1 = np.array(v1)
        self.v2 = np.array(v2)
        self.type = "Triangle"

    def ray_intersect(self, ray_origin, ray_direction):
        ray_origin = np.array(ray_origin)
        ray_direction = np.array(ray_direction)
        
        epsilon = 1e-8
        
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        
        h = np.cross(ray_direction, edge2)
        a = np.dot(edge1, h)
        
        if -epsilon < a < epsilon:
            return None
            
        f = 1.0 / a
        s = ray_origin - self.v0
        u = f * np.dot(s, h)
        
        if u < 0.0 or u > 1.0:
            return None
            
        q = np.cross(s, edge1)
        v = f * np.dot(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return None
            
        t = f * np.dot(edge2, q)
        
        if t > epsilon:
            point = ray_origin + ray_direction * t
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)
            
            return {
                'distance': t,
                'point': point,
                'normal': normal,
                'material': self.material,
                'obj': self
            }
            
        return None

class Cube(Shape):
    def __init__(self, position, size, material):
        super().__init__(position, material)
        self.position = np.array(position)
        self.size = size
        self.type = "Cube"

    def ray_intersect(self, ray_origin, ray_direction):
        ray_origin = np.array(ray_origin)
        ray_direction = np.array(ray_direction)
        
        half_size = self.size / 2
        min_bounds = self.position - half_size
        max_bounds = self.position + half_size
        
        tmin = (min_bounds - ray_origin) / ray_direction
        tmax = (max_bounds - ray_origin) / ray_direction
        
        t1 = np.minimum(tmin, tmax)
        t2 = np.maximum(tmin, tmax)
        
        tnear = np.max(t1)
        tfar = np.min(t2)
        
        if tnear > tfar or tfar < 0:
            return None
            
        t = tnear if tnear > 0 else tfar
        if t < 0:
            return None
            
        point = ray_origin + ray_direction * t
        
        normal = np.array([0.0, 0.0, 0.0])
        for i in range(3):
            if abs(point[i] - min_bounds[i]) < 1e-6:
                normal[i] = -1
                break
            elif abs(point[i] - max_bounds[i]) < 1e-6:
                normal[i] = 1
                break
        
        if np.linalg.norm(normal) == 0:
            normal = np.array([1, 0, 0])
        
        return {
            'distance': t,
            'point': point,
            'normal': normal,
            'material': self.material,
            'obj': self
        }
import numpy as np
from obj import Obj

class Model:
    def __init__(self, filename, translate = [0, 0, 0], rotate = [0, 0, 0], scale = [1, 1, 1]):
        self.model = Obj(filename)
        self.translate = translate
        self.rotate = rotate
        self.scale = scale

    def ray_intersect(self, ray_origin, ray_direction):
        min_distance = float('inf')
        intersect = None
        
        for face in self.model.faces:
            vertices = []
            for vertex_index in face:
                vertex = self.model.vertices[vertex_index[0] - 1]
                vertices.append(vertex)
            
            if len(vertices) >= 3:
                hit = self.triangle_intersect(ray_origin, ray_direction, vertices[0], vertices[1], vertices[2])
                if hit and hit['distance'] < min_distance:
                    min_distance = hit['distance']
                    intersect = hit
                    
        return intersect

    def triangle_intersect(self, ray_origin, ray_direction, v0, v1, v2):
        epsilon = 1e-8
        
        edge1 = np.subtract(v1, v0)
        edge2 = np.subtract(v2, v0)
        
        h = np.cross(ray_direction, edge2)
        a = np.dot(edge1, h)
        
        if -epsilon < a < epsilon:
            return None
            
        f = 1.0 / a
        s = np.subtract(ray_origin, v0)
        u = f * np.dot(s, h)
        
        if u < 0.0 or u > 1.0:
            return None
            
        q = np.cross(s, edge1)
        v = f * np.dot(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return None
            
        t = f * np.dot(edge2, q)
        
        if t > epsilon:
            point = np.add(ray_origin, np.multiply(ray_direction, t))
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)
            
            return {
                'distance': t,
                'point': point,
                'normal': normal
            }
            
        return None
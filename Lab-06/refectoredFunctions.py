import numpy as np

def reflect(incident, normal):
    return incident - 2 * np.dot(incident, normal) * normal

def refract(incident, normal, n1, n2):
    eta = n1 / n2
    dot_i = np.dot(incident, normal)
    
    k = 1 - eta**2 * (1 - dot_i**2)
    if k < 0:
        return None
    
    return eta * incident - (eta * dot_i + np.sqrt(k)) * normal

def fresnel(incident, normal, n1, n2):
    cos_i = abs(np.dot(incident, normal))
    
    if n1 > n2:
        eta = n1 / n2
        sin_t_sq = eta**2 * (1 - cos_i**2)
        if sin_t_sq > 1:
            return 1.0
        cos_t = np.sqrt(1 - sin_t_sq)
    else:
        eta = n1 / n2
        cos_t = np.sqrt(1 - eta**2 * (1 - cos_i**2))
    
    r_parallel = ((n2 * cos_i - n1 * cos_t) / (n2 * cos_i + n1 * cos_t))**2
    r_perpendicular = ((n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t))**2
    
    return (r_parallel + r_perpendicular) / 2

def cast_ray_with_reflections(self, origin, direction, recursion=0):
    if recursion >= self.max_recursions:
        return [0, 0, 0]
        
    min_distance = float('inf')
    hit = None
    
    for obj in self.scene:
        intersect = obj.ray_intersect(origin, direction)
        if intersect and intersect['distance'] < min_distance:
            min_distance = intersect['distance']
            hit = intersect
            
    if not hit:
        return self.clear_color
        
    material = hit['material']
    point = hit['point']
    normal = hit['normal']
    
    if material.matType == "REFLECTIVE":
        reflect_dir = reflect(direction, normal)
        reflect_origin = point + normal * 0.001
        reflect_color = self.cast_ray(reflect_origin, reflect_dir, recursion + 1)
        return reflect_color
        
    elif material.matType == "TRANSPARENT":
        kr = fresnel(direction, normal, 1.0, material.ior)
        
        color = [0, 0, 0]
        
        if kr < 1:
            refract_dir = refract(direction, normal, 1.0, material.ior)
            if refract_dir is not None:
                refract_origin = point - normal * 0.001
                refract_color = self.cast_ray(refract_origin, refract_dir, recursion + 1)
                for i in range(3):
                    color[i] += (1 - kr) * refract_color[i]
        
        reflect_dir = reflect(direction, normal)
        reflect_origin = point + normal * 0.001
        reflect_color = self.cast_ray(reflect_origin, reflect_dir, recursion + 1)
        for i in range(3):
            color[i] += kr * reflect_color[i]
            
        return color
        
    else:
        return self.phong_lighting(hit, direction)
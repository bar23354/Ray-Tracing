import numpy as np

EPS = 1e-4

def normalize(v):
    v = np.array(v, dtype=np.float64)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def reflect(incident, normal):
    i = normalize(incident)
    n = normalize(normal)
    return i - 2.0 * np.dot(i, n) * n

def refract(incident, normal, n1, n2):
    i = normalize(incident)
    n = normalize(normal)
    eta = n1 / n2
    cosi = np.dot(i, n)
    k = 1.0 - eta**2 * (1.0 - cosi**2)
    if k < 0:
        return None
    return eta * i - (eta * cosi + np.sqrt(k)) * n

def fresnel(incident, normal, n1, n2):
    i = normalize(incident)
    n = normalize(normal)
    cosi = np.clip(np.dot(i, n), -1.0, 1.0)

    if cosi > 0:
        n1, n2 = n2, n1
        cosi = abs(cosi)
        n = -n
    else:
        cosi = abs(cosi)

    eta = n1 / n2
    sin_t_sq = eta**2 * (1 - cosi**2)
    if sin_t_sq > 1:
        return 1.0
    cos_t = np.sqrt(1 - sin_t_sq)

    r_s = ((n1 * cosi - n2 * cos_t) / (n1 * cosi + n2 * cos_t))**2
    r_p = ((n2 * cosi - n1 * cos_t) / (n2 * cosi + n1 * cos_t))**2

    return np.clip((r_s + r_p) * 0.5, 0.0, 1.0)

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
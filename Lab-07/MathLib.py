import numpy as np
from math import pi, sin, cos, isclose



def TranslationMatrix(x, y, z):
	
	return np.matrix([[1, 0, 0, x],
					  [0, 1, 0, y],
					  [0, 0, 1, z],
					  [0, 0, 0, 1]])



def ScaleMatrix(x, y, z):
	
	return np.matrix([[x, 0, 0, 0],
					  [0, y, 0, 0],
					  [0, 0, z, 0],
					  [0, 0, 0, 1]])



def RotationMatrix(pitch, yaw, roll):
	
	# Convertir a radianes
	pitch *= pi/180
	yaw *= pi/180
	roll *= pi/180
	
	pitchMat = np.matrix([[1,0,0,0],
						  [0,cos(pitch),-sin(pitch),0],
						  [0,sin(pitch),cos(pitch),0],
						  [0,0,0,1]])
	
	yawMat = np.matrix([[cos(yaw),0,sin(yaw),0],
						[0,1,0,0],
						[-sin(yaw),0,cos(yaw),0],
						[0,0,0,1]])
	
	rollMat = np.matrix([[cos(roll),-sin(roll),0,0],
						 [sin(roll),cos(roll),0,0],
						 [0,0,1,0],
						 [0,0,0,1]])
	
	return pitchMat * yawMat * rollMat

def LookAtMatrix(eye, target, up):
    """Matriz de vista - posición de cámara"""
    eye = np.array(eye, dtype=float)
    target = np.array(target, dtype=float)
    up = np.array(up, dtype=float)
    
    forward = target - eye
    forward = forward / np.linalg.norm(forward)
    
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    
    up = np.cross(right, forward)
    
    return np.matrix([
        [right[0], right[1], right[2], -np.dot(right, eye)],
        [up[0], up[1], up[2], -np.dot(up, eye)],
        [-forward[0], -forward[1], -forward[2], np.dot(forward, eye)],
        [0, 0, 0, 1]
    ])

def PerspectiveMatrix(fov, aspect, near, far):
    """Matriz de proyección perspectiva"""
    import math
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    
    return np.matrix([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ])

def ViewportMatrix(x, y, width, height):
    """Matriz de viewport - transformación a coordenadas de pantalla"""
    return np.matrix([
        [width/2, 0, 0, x + width/2],
        [0, -height/2, 0, y + height/2],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

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
import pygame
import numpy as np
from math import pi, tan, atan2, asin, sqrt, acos
from camera import Camera
from figures import Sphere, Material, Plane, Disk, Triangle, Cube
from BMP_Writer import GenerateBMP
from figures import *
from lights import *
from refectoredFunctions import reflect, refract, fresnel, normalize, EPS

class EnvMap:
    def __init__(self, path):
        self.path = path
        self.pixels = None
        self.width = 0
        self.height = 0
        self.load_hdr()
    
    def load_hdr(self):
        try:
            import imageio.v3 as iio
            img = iio.imread(self.path)
            if img is not None:
                self.pixels = img.astype(np.float32)
                self.height, self.width = self.pixels.shape[:2]
                if len(self.pixels.shape) == 2:
                    self.pixels = np.stack([self.pixels] * 3, axis=-1)
                print(f"HDR cargado: {self.width}x{self.height}")
            else:
                self.create_default_env()
        except Exception as e:
            print(f"Error cargando HDR: {e}")
            self.create_default_env()
    
    def create_default_env(self):
        self.width = 512
        self.height = 256
        self.pixels = np.zeros((self.height, self.width, 3), dtype=np.float32)
        for y in range(self.height):
            for x in range(self.width):
                t = y / self.height
                self.pixels[y, x] = [0.5 + 0.5*t, 0.7 + 0.3*t, 1.0]
    
    def get_color(self, u, v):
        if self.pixels is None:
            return [0.5, 0.7, 1.0]
            
        u = u % 1.0
        v = max(0, min(1, v))
        
        x = u * (self.width - 1)
        y = v * (self.height - 1)
        
        x0, x1 = int(x), min(int(x) + 1, self.width - 1)
        y0, y1 = int(y), min(int(y) + 1, self.height - 1)
        
        fx = x - x0
        fy = y - y0
        
        c00 = self.pixels[y0, x0]
        c01 = self.pixels[y0, x1]
        c10 = self.pixels[y1, x0]
        c11 = self.pixels[y1, x1]
        
        color = (c00 * (1 - fx) * (1 - fy) +
                c01 * fx * (1 - fy) +
                c10 * (1 - fx) * fy +
                c11 * fx * fy)
        
        exposure = 0.005
        color = color * exposure
        color = color / (1 + color)
        
        gamma = 1.0 / 2.2
        color = np.power(np.maximum(color, 0), gamma)
        
        return [min(1, max(0, float(c))) for c in color]

class Raytracer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.camera = Camera()
        self.scene = []
        self.lights = []
        self.clear_color = [0, 0, 0]
        self.current_color = [1, 1, 1]
        self.ambient_light = [0.1, 0.1, 0.1]
        self.max_recursions = 5
        self.envMap = None
        
    def get_env_color(self, direction):
        if self.envMap:
            direction = direction / np.linalg.norm(direction)
            
            u = (atan2(direction[0], -direction[2]) + pi) / (2 * pi)
            v = (asin(max(-1, min(1, direction[1]))) + pi/2) / pi
            
            return self.envMap.get_color(u, v)
        return self.clear_color
        
    def glClearColor(self, r, g, b):
        self.clear_color = [r, g, b]
        
    def glColor(self, r, g, b):
        self.current_color = [r, g, b]
        
    def cast_ray(self, origin, direction, recursion=0):
        if recursion >= self.max_recursions:
            return self.get_env_color(direction)
            
        min_distance = float('inf')
        hit = None
        
        for obj in self.scene:
            intersect = obj.ray_intersect(origin, direction)
            if intersect and intersect['distance'] < min_distance:
                min_distance = intersect['distance']
                hit = intersect
                
        if not hit:
            return self.get_env_color(direction)
            
        material = hit['material']
        point = hit['point']
        normal = normalize(hit['normal'])
        direction = normalize(direction)
        
        is_outside = np.dot(direction, normal) < 0
        bias = normal * EPS if is_outside else -normal * EPS
        
        if material.matType == "REFLECTIVE":
            reflect_dir = reflect(direction, normal)
            reflect_origin = point + bias
            reflect_color = self.cast_ray(reflect_origin, reflect_dir, recursion + 1)
            
            tint = np.array(material.diffuse)
            final_color = np.array(reflect_color) * tint
            
            base_lighting = np.array(self.phong_lighting(hit, direction))
            final_color = final_color * 0.95 + base_lighting * 0.05
            
            return [min(1, max(0, c)) for c in final_color]
            
        elif material.matType == "TRANSPARENT":
            n1 = 1.0
            n2 = material.ior
            kr = fresnel(direction, normal, n1, n2)

            color = np.array([0.0, 0.0, 0.0])
            if kr < 1:
                refract_dir = refract(direction, normal, n1, n2)
                if refract_dir is not None:
                    refract_origin = point - bias
                    refract_color = np.array(self.cast_ray(refract_origin, refract_dir, recursion + 1))
                    
                    tint = np.array(material.diffuse)
                    tint = tint * 0.3 + 0.7
                    color += (1 - kr) * refract_color * tint

            reflect_dir = reflect(direction, normal)
            reflect_origin = point + bias
            reflect_color = np.array(self.cast_ray(reflect_origin, reflect_dir, recursion + 1))
            color += kr * reflect_color
            
            base_lighting = np.array(self.phong_lighting(hit, direction))
            color = color * 0.95 + base_lighting * 0.05
                
            return [min(1, max(0, c)) for c in color]
            
        else:
            return self.phong_lighting(hit, direction)
    
    def cast_ray_simple(self, origin, direction):
        min_distance = float('inf')
        hit = None
        
        for obj in self.scene:
            intersect = obj.ray_intersect(origin, direction)
            if intersect and intersect['distance'] < min_distance:
                min_distance = intersect['distance']
                hit = intersect
                
        return hit
    
    def cast_shadow_ray(self, origin, direction, max_distance):
        for obj in self.scene:
            intersect = obj.ray_intersect(origin, direction)
            if intersect:
                d = intersect['distance']
                if d > EPS and d < max_distance:
                    return True
        return False
    
    def phong_lighting(self, hit, ray_direction):
        material = hit['material']
        point = hit['point']
        normal = hit['normal']
        
        final_color = [0, 0, 0]
        
        ambient_factor = 2.0 if material.matType == "REFLECTIVE" else 1.0
        for i in range(3):
            final_color[i] += self.ambient_light[i] * material.diffuse[i] * ambient_factor
        
        for light in self.lights:
            if light.lightType == "Directional":
                light_dir = np.array([-x for x in light.direction])
                light_dir = light_dir / np.linalg.norm(light_dir)
                
                shadow_origin = point + normal * EPS
                in_shadow = self.cast_shadow_ray(shadow_origin, light_dir, float('inf'))
                
                if not in_shadow:
                    diffuse_intensity = max(0, np.dot(normal, light_dir))
                    
                    for i in range(3):
                        final_color[i] += (diffuse_intensity * 
                                         material.diffuse[i] * 
                                         light.color[i] * 
                                         light.intensity)
                    
                    if material.ks > 0:
                        view_dir = np.array([-x for x in ray_direction])
                        view_dir = view_dir / np.linalg.norm(view_dir)
                        
                        reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
                        reflect_dir = reflect_dir / np.linalg.norm(reflect_dir)
                        
                        spec_intensity = max(0, np.dot(view_dir, reflect_dir)) ** material.spec
                        
                        specular_color = [1.0, 1.0, 1.0]
                        for i in range(3):
                            final_color[i] += (material.ks * 
                                             spec_intensity * 
                                             specular_color[i] * 
                                             light.intensity)
        
        return [min(1, max(0, c)) for c in final_color]
    
    def render_to_bmp(self, filename="raytraced.bmp"):
        framebuffer = []
        
        print(f"Renderizando imagen {self.width}x{self.height}...")
        
        fov = 60
        aspect_ratio = self.width / self.height
        fov_radians = fov * pi / 180
        scale = tan(fov_radians / 2)
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                px = (2 * (x + 0.5) / self.width - 1) * aspect_ratio * scale
                py = (1 - 2 * (y + 0.5) / self.height) * scale
                
                direction = np.array([px, py, -1])
                direction = direction / np.linalg.norm(direction)
                
                color = self.cast_ray(self.camera.translation, direction)
                
                pixel = (
                    int(min(255, max(0, color[0] * 255))),
                    int(min(255, max(0, color[1] * 255))),
                    int(min(255, max(0, color[2] * 255)))
                )
                    
                row.append(pixel)
            framebuffer.append(row)
            
            if y % 50 == 0:
                print(f"Progreso: {y}/{self.height} líneas")
        
        transposed_buffer = []
        for x in range(self.width):
            column = []
            for y in range(self.height):
                column.append(framebuffer[y][x])
            transposed_buffer.append(column)
        
        GenerateBMP(filename, self.width, self.height, 3, transposed_buffer)
        print(f"Imagen guardada como: {filename}")
        return framebuffer
    
    def render_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ray Tracer 2025")
        clock = pygame.time.Clock()
        running = True
        
        if not hasattr(self, 'lights') or not self.lights:
            self.lights = [DirectionalLight(direction=[-1, -1, -1])]
        
        print("Woah, woah, renderizando... Presiona ESC para salir")
        
        rendered_pixels = 0
        total_pixels = self.width * self.height
        
        indices = [(x, y) for x in range(self.width) for y in range(self.height)]
        
        while running and rendered_pixels < total_pixels:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            fov = 60
            aspect_ratio = self.width / self.height
            fov_radians = fov * pi / 180
            scale = tan(fov_radians / 2)
            
            for _ in range(200):
                if rendered_pixels >= total_pixels:
                    break
                    
                x, y = indices[rendered_pixels]
                
                px = (2 * (x + 0.5) / self.width - 1) * aspect_ratio * scale
                py = (1 - 2 * (y + 0.5) / self.height) * scale
                
                direction = np.array([px, py, -1])
                direction = direction / np.linalg.norm(direction)
                
                color = self.cast_ray(self.camera.translation, direction)
                
                pixel_color = (
                    int(min(255, max(0, color[0] * 255))),
                    int(min(255, max(0, color[1] * 255))),
                    int(min(255, max(0, color[2] * 255)))
                )
                
                screen.set_at((x, self.height - y - 1), pixel_color)
                rendered_pixels += 1
            
            pygame.display.flip()
            clock.tick(60)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    raytracer = Raytracer(800, 600)
    
    raytracer.envMap = EnvMap("assets/viale_giuseppe_garibaldi_4k.hdr")
    raytracer.glClearColor(0.1, 0.3, 0.5)
    
    wallMaterial = Material(diffuse=[0.8, 0.8, 0.9], spec=16, ks=0.2, matType="OPAQUE")
    floorMaterial = Material(diffuse=[0.6, 0.4, 0.3], spec=32, ks=0.3, matType="OPAQUE")
    ceilingMaterial = Material(diffuse=[0.9, 0.9, 0.8], spec=8, ks=0.1, matType="OPAQUE")
    
    redCube = Material(diffuse=[0.8, 0.2, 0.2], spec=64, ks=0.4, matType="OPAQUE")
    blueCube = Material(diffuse=[0.2, 0.2, 0.8], spec=64, ks=0.4, matType="REFLECTIVE")
    
    triangleMaterial = Material(diffuse=[0.2, 0.8, 0.2], spec=128, ks=0.6, matType="REFLECTIVE")
    diskMaterial = Material(diffuse=[0.9, 0.9, 0.9], spec=128, ks=0.1, matType="TRANSPARENT", ior=1.5)
    
    floor = Plane([0, -3, 0], [0, 1, 0], floorMaterial)
    ceiling = Plane([0, 3, 0], [0, -1, 0], ceilingMaterial)
    backWall = Plane([0, 0, -8], [0, 0, 1], wallMaterial)
    leftWall = Plane([-5, 0, 0], [1, 0, 0], wallMaterial)
    rightWall = Plane([5, 0, 0], [-1, 0, 0], wallMaterial)
    
    cube1 = Cube([-2, -1.5, -5], 1.5, redCube)
    cube2 = Cube([2.5, -2, -6], 1, blueCube)
    
    triangle = Triangle([-1, 1, -4], [1, 1, -4], [0, 2.5, -4], triangleMaterial)
    
    disk = Disk([0, 0, -3], [0, 0, 1], 0.8, diskMaterial)

    raytracer.scene = [floor, ceiling, backWall, leftWall, rightWall, cube1, cube2, triangle, disk]
    raytracer.lights = [
        DirectionalLight(color=[1, 1, 1], intensity=1.0, direction=[-1, -1, -1]),
        DirectionalLight(color=[0.8, 0.8, 1.0], intensity=0.5, direction=[1, 0.5, -0.5])
    ]
    
    raytracer.render_pygame()
    
    print("\nBMP...")
    raytracer.render_to_bmp("RoomScene.bmp")
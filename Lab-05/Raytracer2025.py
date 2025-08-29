import pygame
import numpy as np
from math import pi, tan
from camera import Camera
from figures import Sphere, Material
from BMP_Writer import GenerateBMP
from figures import *
from lights import *

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
        
    def glClearColor(self, r, g, b):
        self.clear_color = [r, g, b]
        
    def glColor(self, r, g, b):
        self.current_color = [r, g, b]
        
    def cast_ray(self, origin, direction):
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
            if intersect and 0.001 < intersect['distance'] < max_distance:
                return True
        return False
    
    def phong_lighting(self, hit, ray_direction):
        material = hit['material']
        point = hit['point']
        normal = hit['normal']
        
        final_color = [0, 0, 0]
        
        for i in range(3):
            final_color[i] += self.ambient_light[i] * material.diffuse[i]
        
        for light in self.lights:
            if light.lightType == "Directional":
                light_dir = np.array([-x for x in light.direction])
                light_dir = light_dir / np.linalg.norm(light_dir)
                
                shadow_origin = point + normal * 0.001
                in_shadow = self.cast_shadow_ray(shadow_origin, light_dir, float('inf'))
                
                if not in_shadow:
                    diffuse_intensity = max(0, np.dot(normal, light_dir))
                    
                    for i in range(3):
                        final_color[i] += (diffuse_intensity * 
                                         material.diffuse[i] * 
                                         light.color[i] * 
                                         light.intensity)
                    
                    if material.ks > 0 and diffuse_intensity > 0:
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
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                px = (x + 0.5) / self.width * 2 - 1
                py = (y + 0.5) / self.height * 2 - 1
                
                direction = np.array([px, py, -1])
                direction = direction / np.linalg.norm(direction)
                
                hit = self.cast_ray(self.camera.translation, direction)
                
                if hit:
                    color = self.phong_lighting(hit, direction)
                    pixel = (
                        int(color[0] * 255),
                        int(color[1] * 255),
                        int(color[2] * 255)
                    )
                else:
                    clear = self.clear_color
                    pixel = (
                        int(clear[0] * 255),
                        int(clear[1] * 255),
                        int(clear[2] * 255)
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
            
            for _ in range(100):
                if rendered_pixels >= total_pixels:
                    break
                    
                x, y = indices[rendered_pixels]
                
                px = (x + 0.5) / self.width * 2 - 1
                py = (y + 0.5) / self.height * 2 - 1
                
                direction = np.array([px, py, -1])
                direction = direction / np.linalg.norm(direction)
                
                hit = self.cast_ray(self.camera.translation, direction)
                
                if hit:
                    color = self.phong_lighting(hit, direction)
                    pixel_color = (
                        int(color[0] * 255),
                        int(color[1] * 255),
                        int(color[2] * 255)
                    )
                else:
                    clear = self.clear_color
                    pixel_color = (
                        int(clear[0] * 255),
                        int(clear[1] * 255),
                        int(clear[2] * 255)
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
    raytracer = Raytracer(600, 600)
    
    raytracer.glClearColor(0.1, 0.3, 0.5)
    
    carbonMaterial = Material(diffuse=[0.15, 0.15, 0.15], spec=8, ks=0.2)
    mickeyRedMaterial = Material(diffuse=[0.8, 0.1, 0.1], spec=64, ks=0.6)
    shoeYellowMaterial = Material(diffuse=[1.0, 0.9, 0.2], spec=128, ks=0.8)
    
    mmHead = Sphere([0, 0, -4], 1.0, carbonMaterial)
    mmLeftEar = Sphere([-0.7, 0.7, -3.8], 0.5, mickeyRedMaterial)
    mmRightEar = Sphere([0.7, 0.7, -3.8], 0.5, shoeYellowMaterial)

    raytracer.scene = [mmHead, mmLeftEar, mmRightEar]
    raytracer.lights = [
        DirectionalLight(color=[1, 1, 1], intensity=1.0, direction=[-1, -1, -1]),
        DirectionalLight(color=[0.6, 0.6, 0.8], intensity=0.3, direction=[1, 0.5, -0.5])
    ]
    
    raytracer.render_pygame()
    
    print("\nBMP...")
    raytracer.render_to_bmp("MouseAlwaysWins.bmp")
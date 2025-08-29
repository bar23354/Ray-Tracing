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
        self.clear_color = [0, 0, 0]
        self.current_color = [1, 1, 1]
        
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
    
    def render_to_bmp(self, filename="raytraced_output.bmp"):
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
                    color = hit['material'].diffuse
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
        self.lights = getattr(self, 'lights', [])
        self.lights.append(DirectionalLight(direction = [-1,-1,-1]))
        
        print("Renderizando en tiempo real... Presiona ESC para salir")
        
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
                    color = hit['material'].diffuse
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
    raytracer = Raytracer(400, 400)
    
    raytracer.glClearColor(0.2, 0.2, 0.3)
    
    red_material = Material(diffuse=[0.8, 0.2, 0.2])
    green_material = Material(diffuse=[0.2, 0.8, 0.2])
    blue_material = Material(diffuse=[0.2, 0.2, 0.8])
    
    sphere1 = Sphere([0, 0, -3], 0.6, red_material)
    sphere2 = Sphere([-1.2, 0, -4], 0.4, green_material)
    sphere3 = Sphere([1.2, 0, -4], 0.4, blue_material)
    
    raytracer.scene = [sphere1, sphere2, sphere3]
    
    raytracer.render_pygame()
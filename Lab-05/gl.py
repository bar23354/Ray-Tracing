import numpy as np
from math import isclose, floor, ceil, tan, pi
from camera import Camera
import random
import pygame

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()
        
        self.camera = Camera()
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)

        self.glClear()

        self.scene = []

    def glClear(self):
        color = [int(i * 255) for i in self.clearColor]
        self.screen.fill(color)

        self.frameBuffer = [[color for y in range(self.height)]
                            for x in range(self.width)]

    def glViewport(self, x, y, width, height):
        self.vpX = round(x)
        self.vpY = round(y)
        self.vpWidth = round(width)
        self.vpHeight = round(height)

        self.viewportMatrix = np.matrix([[width/2, 0, 0, x + width/2],
                                          [0, height/2, 0, y + height/2],
                                          [0, 0, 0, 1]])

    def glProjection(self, n = 0.1, f = 1000, fov = 60):
        aspectRatio = self.vpWidth / self.vpHeight
        fov *= pi/180
        self.topEdge = tan(fov / 2) * n
        self.rightEdge = self.topEdge * aspectRatio

        self.nearPlane = n
        self.farPlane = f

        self.projectionMatrix = np.matrix([[n/self.rightEdge, 0, 0, 0],
                                           [0, n/self.topEdge, 0, 0],
                                           [0, 0, (f + n) / (n - f), -(2 * f * n) / (f - n)],
                                           [0, 0, -1, 0]])
        
    def glClearColor(self, r, g, b):
        self.clearColor = (r, g, b)

    def glColor(self, r, g, b):
        self.color = (r, g, b)

    def glPoint(self, x, y, color = None):
        x = round(x)
        y = round(y)

        if (0 <= x < self.width) and (0 <= y < self.height):
            color = [int(i * 255) for i in (color or self.color)]

            self.screen.set_at((x, self.height - y - 1), color)

            self.frameBuffer[x][y] = color

    def glLine(self, p0, p1, color = None):
        x0 = p0[0]
        y0 = p0[1]
        x1 = p1[0]
        y1 = p1[1]

        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0)
            return
        
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.75
        m = dy / dx if dx != 0 else 0
        y = y0

        for x in range(round(x0), round(x1) + 1):
            if steep:
                self.glPoint(y, x, self.color)
            else:
                self.glPoint(x, y, self.color)

            offset += m

            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1
                
                limit += 1

    def glRender(self):
        indices = [(i, j) for i in range(self.vpWidth) for j in range(self.vpHeight)]

        random.shuffle(indices)

        for i, j in indices:
            x = i + self.vpX
            y = j + self.vpY

            if 0 <= x < self.width and 0 <= y < self.height:
                pX = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                pY = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1

                pX *= self.rightEdge
                pY *= self.topEdge
                pZ = -self.nearPlane

                dir = np.array([pX, pY, pZ])
                dir = dir / np.linalg.norm(dir)

                hit = self.glCastRay(self.camera.translation, dir)

                if hit:
                    color = hit['material'].diffuse
                    self.glPoint(x, y, color)
                    pygame.display.flip()

    def glCastRay(self, origin, direction):
        min_distance = float('inf')
        hit = None

        for obj in self.scene:
            intersect = obj.ray_intersect(origin, direction)
            if intersect and intersect['distance'] < min_distance:
                min_distance = intersect['distance']
                hit = intersect
                
        return hit
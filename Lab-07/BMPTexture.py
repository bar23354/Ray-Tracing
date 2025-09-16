import struct
import numpy as np

class Texture:
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        with open(self.path, "rb") as image:
            image.seek(2)
            self.header_size = struct.unpack("=l", image.read(4))[0]
            image.seek(10)
            self.data_offset = struct.unpack("=l", image.read(4))[0]
            image.seek(18)
            self.width = struct.unpack("=l", image.read(4))[0]
            self.height = struct.unpack("=l", image.read(4))[0]
            image.seek(28)
            self.bpp = struct.unpack("=h", image.read(2))[0]

            image.seek(self.data_offset)

            self.framebuffer = []
            for y in range(self.height):
                self.framebuffer.append([])
                for x in range(self.width):
                    b = ord(image.read(1)) / 255
                    g = ord(image.read(1)) / 255
                    r = ord(image.read(1)) / 255
                    self.framebuffer[y].append([r, g, b])

    def get_color(self, tx, ty):
        if 0 <= tx < 1 and 0 <= ty < 1:
            x = int(tx * self.width)
            y = int(ty * self.height)
            
            if 0 <= x < self.width and 0 <= y < self.height:
                return self.framebuffer[y][x]
        
        return [1, 1, 1]
import numpy as np
from MathLib import TranslationMatrix, RotationMatrix

class Camera:
    def __init__(self):
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def get_view_matrix(self):
        cam_matrix = TranslationMatrix(self.translation[0], self.translation[1], self.translation[2])
        cam_matrix = cam_matrix * RotationMatrix(self.rotation[0], self.rotation[1], self.rotation[2])
        return np.linalg.inv(cam_matrix)

    def translate(self, x, y, z):
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def rotate(self, x, y, z):
        self.rotation[0] += x
        self.rotation[1] += y
        self.rotation[2] += z
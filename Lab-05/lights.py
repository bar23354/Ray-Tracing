import numpy as np

class Light(object):
    def __init__(self, color = [1,1,1], intensity = 1.0, lightType = "None"):
        self.color = color
        self.intensity = intensity
        self.lightType = lightType

    def GetLightColor(self):
        return [(i * self.intensity) for i in self.color]
    
class DirectionalLight(Light):
    def __init__(self, color = [1,1,1], intensity = 1.0, direction = [0,-1,0]):
        super().__init__(color, intensity, "Directional")
        self.direction = direction / np.linalg.norm(direction)

    def GetLightColor(self, intercept = None):
        lightColor = super().GetLightColor()

        if intercept:
        # surfaceIntensity = NORMAL o -LIGHT
            dir = [(i * -1) for i in self.direction]
            surfaceIntensity = np.dot(intercept.normal, dir)
            surfaceIntensity = max(0, min(1, surfaceIntensity))
            lightColor = [(i * surfaceIntensity) for i in lightColor]

        return lightColor

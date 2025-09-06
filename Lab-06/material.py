class Material(object):
    def __init__(self, diffuse = [1,1,1]):
        self.diffuse = diffuse

    def GetSurfaceColor(self, interrcept, renderer):

        # Phong reflection model
        # LightColors = LightColor + Specular
        # FinalColor = DiffuseColor * LightColor

        lightColor = [0,0,0]
        finalColor = self.diffuse

        finalColor = [(finalColor[i] * lightColor[i] for i in range(3))]
        finalColor = [min(1, finalColor[i]) for i in range(3)]

        return finalColor

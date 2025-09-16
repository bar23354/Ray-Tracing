class Intercept(object):
    def __init__(self, distance, point, normal, rayDirection, obj):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.rayDirection = rayDirection
        self.obj = obj
class Obj:
    def __init__(self, filename):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        self.read(filename)

    def read(self, filename):
        with open(filename, "r") as file:
            lines = file.read().splitlines()

        for line in lines:
            words = line.split(' ')
            words = [word for word in words if word != '']

            if len(words) > 0:
                if words[0] == 'v':
                    self.vertices.append([float(words[1]), float(words[2]), float(words[3])])

                elif words[0] == 'vt':
                    u = float(words[1]) if len(words) > 1 else 0
                    v = float(words[2]) if len(words) > 2 else 0
                    self.texcoords.append([u, v])

                elif words[0] == 'vn':
                    self.normals.append([float(words[1]), float(words[2]), float(words[3])])

                elif words[0] == 'f':
                    face = []
                    for i in range(1, len(words)):
                        w = words[i].split('/')
                        face.append([
                            int(w[0]) if w[0] else None,
                            int(w[1]) if len(w) > 1 and w[1] else None,
                            int(w[2]) if len(w) > 2 and w[2] else None
                        ])
                    self.faces.append(face)
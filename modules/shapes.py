class tetrisShape():
    def __init__(self, shape=0):
        self.shape_empty = 0
        self.shape_I = 1
        self.shape_L = 2
        self.shape_J = 3
        self.shape_T = 4
        self.shape_O = 5
        self.shape_S = 6
        self.shape_Z = 7
        self.shape_relative_coords = [[0,0], [0,0], [0,0], [0,0]], [[0,-1], [0,0], [0,1], [0,2]], [[0,-1], [0,0], [0,1], [1,1]], [[0,-1], [0,0], [0,1], [-1,1]], [[0,-1], [0,0], [0,1], [1,0]], [[0,0], [0,-1], [1,0], [1,-1]], [[0,0], [0,-1], [-1,0], [1,-1]], [[0,0], [0,-1], [1,0], [-1,-1]]
        self.shape = shape
        self.relative_coords = self.shape_relative_coords[self.shape]

    def getRotatedRelativeCoords(self, direction):
        if direction == 0 or self.shape == self.shape_O:
            return self.relative_coords
        if direction == 1:
            return [[-y, x] for x, y in self.relative_coords]
        if direction == 2:
            if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
                return self.relative_coords
            else:
                return [[-x, -y] for x, y in self.relative_coords]
        if direction == 3:
            if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
                return [[-y, x] for x, y in self.relative_coords]
            else:
                return [[y, -x] for x, y in self.relative_coords]

    def getAbsoluteCoords(self, direction, x, y):
        return [[x+i, y+j] for i, j in self.getRotatedRelativeCoords(direction)]

    def getRelativeBoundary(self, direction):
        relative_coords_now = self.getRotatedRelativeCoords(direction)
        xs = [i[0] for i in relative_coords_now]
        ys = [i[1] for i in relative_coords_now]
        return min(xs), max(xs), min(ys), max(ys)

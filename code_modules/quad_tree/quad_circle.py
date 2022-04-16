class QuadCircle:
    def __init__(self, x, y, radius) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.rSquared = self.radius * self.radius

        self.type = "Circle"

    def contains(self, p):
        return getDistanceSquaredPointVsPoint((self.x, self.y), (p.x, p.y)) < self.radius**2    

    def intersects(self, range):
        return getDistanceSquaredPointVsPoint((self.x, self.y), (range.x, range.y)) < (self.radius + range.radius)**2


def getDistanceSquaredPointVsPoint(p1, p2):
    distanceSquared = (
        (p1[0] - p2[0]) * (p1[0] - p2[0]) + 
        (p1[1] - p2[1]) * (p1[1] - p2[1])
    )
    return distanceSquared
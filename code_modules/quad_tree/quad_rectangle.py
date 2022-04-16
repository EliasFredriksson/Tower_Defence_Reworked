class QuadRectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.type = "Rect"

    def contains(self, p):
        return (
            p.x >= self.x and
            p.x <= self.x + self.w and
            p.y >= self.y and
            p.y <= self.y + self.h
            )

    def intersects(self, range):
        if range.type == "Circle":
            Xn = max(self.x, min(range.x, (self.x + self.w)))
            Yn = max(self.y, min(range.y, (self.y + self.h)))

            Dx = Xn - range.x
            Dy = Yn - range.y
            return (Dx**2 + Dy**2) <= range.radius**2
        else:
            return not (
                range.x > self.x + self.w or
                range.x + range.w < self.x or
                range.y > self.y + self.h or
                range.y + range.h < self.y )
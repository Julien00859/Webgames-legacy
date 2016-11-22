from math import sin, cos, sqrt

class Point:
    def __init__(self, posx: int, posy: int):
        self.x = posx
        self.y = posy

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __repr__(self) -> str:
        return "<Point(x={}, y={})>".format(self.x, self.y)


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.a = (p1.y - p2.y) / (p1.x - p2.x) if p1.x - p2.x != 0 else float("inf")
        self.b = p1.y - self.a * p1.x

    def __str__(self) -> str:
        return "y = {}*x + {}".format(self.a, self.b)

    def __repr__(self) -> str:
        return "<Line(a={}, b={})>".format(self.a, self.b)

    def __call__(self, x: float) -> float:
        return self.a * x + self.b

    def __lt__(self, point: Point) -> bool:
        return self(point.x) < point.y

    def __gt__(self, point: Point) -> bool:
        return self(point.x) > point.y

    def __eq__(self, line) -> bool:
        return self(point.x) == point.y

class Vector:
    def __init__(self, direction: float, length: float):
        self.direction = direction
        self.length = length

    def __call__(self, begin: Point) -> Point:
        return Point(begin.x + cos(self.direction) * self.length,
                     begin.y + sin(self.direction) * self.length)

class RectRange:
    def __init__(self, p1: Point, p2: Point, radius=0.0):
        self.min = Point(min(p1.x, p2.x) - radius, min(p1.y, p2.y) - radius)
        self.max = Point(max(p1.x, p2.x) + radius, max(p1.y, p2.y) + radius)

    def __str__(self) -> str:
        return "([{}:{}, {}:{}])".format(self.min.x, self.max.x, self.min.y, self.max.y)

    def __repr__(self) -> str:
        return "<RectRange(From:{}, To:{})>".format(repr(self.min), repr(self.max))

    def __contains__(self, point: Point) -> bool:
        return self.min.x <= point.x <= self.max.x and self.min.y <= point.y <= self.max.y

class Cercle:
    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

    def __repr__(self) -> str:
        return "<Cercle(Center:{}, Radius:{})>".format(self.center, self.radius)

    def inter(self, other: object) -> bool:
        dx = self.center.x + self.radius - other.center.x - other.radius
        dy = self.center.y + self.radius - other.center.y - other.radius

        dist = sqrt(dx ** 2 + dy ** 2)

        return dist < self.radius + other.radius
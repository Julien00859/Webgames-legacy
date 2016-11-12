from math import sin, cos

class Point:
    def __init__(self, posx: int, posy: int):
        self.x = posx
        self.y = posy

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "<Point(x={}, y={})>".format(self.x, self.y)

    def __eq__(self, point):
        return point.x == self.x and point.y == self.y


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.a = (p1.y - p2.y) / (p1.x - p2.x)
        self.b = p1.y - self.a * p1.x

    def __str__(self) -> str:
        return "y = {}*x + {}".format(self.a, self.b)

    def __repr__(self) -> str:
        return "<Line(a={}, b={})>".format(self.a, self.b)

    def __call__(self, x: float) -> float:
        return self.a * x + self.b

    def __lt__(self, point: Point) -> bool:
        return self(point.x) < point.y

    def __le__(self, point: Point) -> bool:
        return self.__lt__(point) or self.__contains__(point)

    def __gt__(self, point: Point) -> bool:
        return self(point.x) > point.y

    def __ge__(self, point: Point) -> bool:
        return self.__gt__(point) or self.__contains__(point)

    def __contains__(self, point: Point) -> bool:
        return self(point.x) == point.y

    def __eq__(self, line) -> bool:
        return self.a == line.a and self.b == line.b

class Vector:
    def __init__(self, direction: float, length: float):
        self.direction = direction
        self.length = length

    def __call__(self, begin: Point) -> Point:
        return Point(begin.x + cos(self.direction) * self.length,
                     begin.y + sin(self.direction) * self.length)

class Rectangle:
    def __init__(self, p1: Point, p2: Point, radius=0):
        self.p1 = Point(min(p1.x, p2.x) - radius, min(p1.y, p2.y) - radius)
        self.p2 = Point(max(p1.x, p2.x) + radius, max(p1.y, p2.y) + radius)

    def __str__(self) -> str:
        return "([{}:{}, {}:{}])".format(self.p1.x, self.p2.x, self.p1.y, self.p2.y)

    def __repr__(self) -> str:
        return "<RectRange(From:{}, To:{})>".format(repr(self.p1), repr(self.p2))

    def __contains__(self, point: Point) -> bool:
        return self.p1.x <= point.x <= self.p2.x and self.p1.y <= point.y <= self.p2.y
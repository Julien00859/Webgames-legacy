from game_server.games.robotwar.settings import *
from utils.geometry import *
from exceptions import GameException

from math import pi as PI, sin, cos, sqrt
import logging

logger = logging.getLogger(__name__)


class IsDead(GameException):
    pass

class GameValueError(GameException):
    pass

class GameTypeError(GameException):
    pass


class Entity:
    size = 0
    radius = lambda self: self.size / 2

    def __init__(self, position: Point, direction: float, speed: float):
        self.position = position
        self.direction = direction
        self.speed = speed
        self.is_alive = True
        self.is_moving = False


    def move(self, max_x: int, max_y: int) -> int:
        origin = Point(self.position.x, self.position.y)

        destination = Point(self.position.x + cos(self.direction) * self.speed,
                            self.position.y + sin(self.direction) * self.speed)

        battlefield = RectRange(Point(0, 0), Point(max_x, max_y), -self.radius())

        if destination in battlefield:
            self.position = destination

        else:
            if destination.x < self.radius():
                self.position.x = self.radius()
            elif destination.x > max_x - self.radius():
                self.position.x = max_x - self.radius()

            if destination.y < self.radius():
                self.position.y = self.radius()
            elif destination.y > max_y - self.radius():
                self.position.y = max_y - self.radius()


        return sqrt((origin.x - self.position.x) ** 2 + (origin.y - self.position.y) ** 2)

    def check_move(self, entities: list) -> object:
        origin = Circle(self.position, self.size / 2)
        movement = Vector(self.direction, self.speed)
        destination = Circle(movement(origin.center), origin.radius)

        rectangle = RectRange(origin.center, destination.center, origin.radius)

        vector_left = Vector(self.direction - PI / 4, self.size / 2)
        vector_right = Vector(self.direction + PI / 4, self.size / 2)

        line_left = Line(vector_left(origin.center), vector_left(destination.center))
        line_right = Line(vector_right(origin.center), vector_right(destination.center))

        for entity in entities:
            other = Circle(entity.position, entity.size / 2)

            vector_right.length = other.radius
            vector_left.length = other.radius

            other_left = vector_left(other.center)
            other_right = vector_right(other.center)

            if destination.inter(other):
                return entity

            if other_left in rectangle or other_right in rectangle:
                if all(map(lambda point: point < line_left and point < line_right, [other_left, other_right])) or \
                   all(map(lambda point: point > line_left and point > line_right, [other_left, other_right])):
                   continue
                else:
                    return entity

        return None


    def die(self, **kwargs) -> None:
        self.is_alive = False
        self.is_moving = False

    def __str__(self) -> str:
        return "<Entity>"


class Robot(Entity):
    size = 20
    def __init__(self, position: Point):
        super().__init__(position, 0, ROBOT_SPEED)
        self.turret_angle_updated = False
        self.turret_angle = 0
        self.health = 10
        self.attack_speed = ROBOT_ATTACK_SPEED
        self.last_attack = 0
        self.is_alive = True
        self.is_moving = False
        self.is_shooting = False
 
    def event_shoot(self, *args, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")
        self.is_shooting = True

    def event_stop_shooting(self, *args, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")
        self.is_shooting = False

    def event_move(self, direction: float, *args, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")

        if not (-2 * PI <= direction <= 2 * PI):
            raise GameValueError("'direction' value must be between 0 and 2 * PI")
        self.direction = direction
        self.is_moving = True

    def event_stop_moving(self, *args, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")
        self.is_moving = False

    def event_rotate(self, angle: float, *args, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")
        if not (-2 * PI <= angle <= 2 * PI):
            raise GameValueError("'direction' value must be between 0 and 2 * PI")
        self.turret_angle_updated = True
        self.turret_angle = angle


    def hit(self) -> None:
        if not self.is_alive:
            logger.warn("Player hit while dead")
            return
            
        self.health -= 1
        if self.health <= 0:
            self.die()


    def move(self, max_x, max_y, other_robots=None) -> int:
        if other_robots is None or self.check_move(other_robots) is None:
            return super().move(max_x, max_y)
        return 0

    def die(self) -> None:
        super().die()
        self.is_shooting = False

    def __str__(self) -> str:
        return "<Robot>"


class Bullet(Entity):
    size = 2
    def __init__(self, shooter: Robot):
        canon = Vector(shooter.turret_angle, shooter.size * 0.6)(shooter.position)
        super().__init__(canon, shooter.turret_angle, BULLET_SPEED)
        self.shooter = shooter
        self.wall_hit = 0


    def move(self, max_x, max_y, robots=None) -> Robot:
        if self.is_alive:
            dest = Vector(self.direction, self.speed)(self.position)

            robot = self.check_move(robots) if robots is not None else None
            if robot is None:
                speed = self.speed
                distances = []
                while True:
                    distances.append(super().move(max_x, max_y))
                    if sum(distances) < speed * 0.9:
                        self.speed -= distances[-1]
                        self.wall_hit += 1
                        if (self.position.x == self.radius() or self.position.x == max_x - self.radius()):
                            self.direction -= 2 * (self.direction - PI / 2)

                        else:
                            self.direction = -self.direction

                        logger.info("sum: %d, speed: %d", sum(distances), speed)

                    else:
                        self.speed = speed
                        break

            else:
                logger.info("Hit!")
                self.die()
                robot.hit()
                return robot

            self.speed -= BULLET_FRICTION * (self.wall_hit + 1)
            if self.speed <= 0:
                self.die()
        else:
            logger.warn("Dead bullet tried to move")

        return None

    def __str__(self) -> str:
        return "<Bullet>"


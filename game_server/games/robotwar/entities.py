from game_server.games.robotwar.settings import *
from game_server.games.robotwar.geometry import *
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
    def __init__(self, position: list, direction: float, speed: float):
        self.position = Point(*position)
        self.direction = direction
        self.speed = speed
        self.is_alive = True
        self.is_moving = False


    def move(self, max_x: int, max_y: int) -> int:
        posx = self.position.x
        posy = self.position.y

        dest_x = self.position.x + cos(self.direction) * self.speed
        dest_y = self.position.y + sin(self.direction) * self.speed

        if dest_x - self.size / 2 < 0:
            self.position.x = self.size / 2
        elif dest_x + self.size / 2 > max_x:
            self.position.x = max_x - self.size / 2
        else:
            self.position.x = dest_x

        if dest_y - self.size / 2 < 0:
            self.position.y = self.size / 2
        elif dest_y + self.size / 2 > max_y:
            self.position.y = max_y - self.size / 2
        else:
            self.position.y = dest_y

        return sqrt((posx - self.position.x) ** 2 + (posy - self.position.y) ** 2)

    def check_move(self, blocking_entities: list) -> Entity:

        # Compute the destination
        dest = Vector(self.direction, self.speed)(self.position)

        for entity in blocking_entities:
            logger.debug("Quick position check %s in %s", entity.position, rect)

            # Compute a rectangle containing both the current entity and the destination 
            rect = Rectangle(self.position, dest)
            rect.p1.x -= self.size / 2
            rect.p1.y -= self.size / 2
            rect.p2.x += self.size / 2
            rect.p2.y += self.size / 2

            if entity.position in rect:
                logger.debug("Deep position check for same values")

                # Compute a vector for my left and right hand
                v_left = Vector(self.direction - PI / 4, self.size / 2)
                v_right = Vector(self.direction + PI / 4, self.size / 2)

                # Compute the two lines for my left and right hand to move to the destination
                l_left = Line(v_left(self.position), v_left(dest))
                l_right = Line(v_right(self.position), v_right(dest))

                # Update the vectors to fit the size of the other robot
                v_left.lenght = entity.size / 2
                v_right.lenght = entity.size / 2

                # Compute the left and right hand of the other robot
                h_left = v_left(entity.position)
                h_right = v_right(entity.position)

                # Block if one of the hand of the other robot is in the "corridor" between l_left and l_right
                if not ((l_left < h_left and l_left < h_right and l_right < h_left and l_right < h_right) or (
                         l_left > h_left and l_left > h_right and l_right > h_left and l_right > h_right)):
                    logger.debug("Blocked by %s", repr(other_robot.position))
                    return entity

        return None



    def die(self, **kwargs) -> None:
        self.is_alive = False
        self.is_moving = False
        self.is_shooting = False


class Robot(Entity):
    size = 20
    def __init__(self, position: list):
        super().__init__(position, 0, ROBOT_SPEED)
        self.turret_angle = 0
        self.health = 10
        self.attack_speed = ROBOT_ATTACK_SPEED
        self.last_attack = 0
        self.is_alive = True
        self.is_moving = False
        self.is_shooting = False

    def check_if_alive(self, func):
        def wrapped(self, *args, **kwargs):
            if not self.is_alive:
                raise IsDead("Dead player cannot shoot")
            func(*args, **kwargs)
        return wrapped

    def check_valid_angle(self, func):
        def wrapped(self, *args, **kwargs):
            if (direction < 0 or direction > PI * 2):
                raise GameValueError("'direction' should be between 0 and 2*pi")
    
    @self.check_if_alive
    def event_shoot(self, *args, **kwargs) -> None:
        self.is_shooting = True

    @self.check_if_alive        
    def event_stop_shooting(self, *args, **kwargs) -> None:
        self.is_shooting = False

    @self.check_if_alive
    @self.check_valid_angle
    def event_move(self, direction: float, *args, **kwargs) -> None:
        self.direction = direction
        self.is_moving = True

    @self.check_if_alive
    def event_stop_moving(self, *args, **kwargs) -> None:
        self.is_moving = False

    @self.check_if_alive
    @self.check_valid_angle
    def event_rotate(self, angle: float, *args, **kwargs) -> None:
        self.turret_angle = angle


    def hit(self) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot be hit again")
            
        self.health -= 1
        if self.health <= 0:
            self.die()


    def move(self, max_x, max_y, other_robots=None) -> int:
        if other_robots is None or self.check_move(other_robots) is None:
            return super().move(max_x, max_y)


class Bullet(Entity):
    size = 2
    def __init__(self, shooter: Robot):
        super().__init__(shooter.position, shooter.turret_angle, BULLET_SPEED)
        self.shooter = shooter
        self.wall_hit = 0


    def move(self, max_x, max_y, robots=None) -> Robot:
        if self.is_alive:
            dest = Vector(self.direction, self.speed)(self.position)

            # If there is no robot in the battlefield or no robot was hit by the buller
            if robots is None or (robot = self.check_move(robots)) is None:

                # If the moved bullet hit a wall
                if (dist_traveled = super().move(max_x, max_y)) != self.speed:
                    self.wall_hit += 1
                    if (self.position.x == 0 or self.position.x == sizex):
                        self.direction -= 2 * (self.direction - PI / 2)

                    elif (self.position.y == 0 or self.position.y == sizey):
                        self.direction = -self.direction

                    self.speed -= dist_traveled
                    super().move(max_x, max_y)
                    self.speed += dist_traveled

            else:
                self.die()
                robot.hit()
                return robot

            self.speed -= BULLET_FRICTION * (self.wall_hit + 1)
            if self.speed <= 0:
                self.die()

        return None


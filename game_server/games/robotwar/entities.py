
try:
    from game_server.games.robotwar.settings import *
    from game_server.games.robotwar.entities import *
    from game_server.games.robotwar.geometry import *
except ImportError:
    from settings import *
    from entities import *
    from geometry import *

from math import pi as PI, sin, cos
import logging

logger = logging.getLogger(__name__)


class IsDead(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Entity:
    def __init__(self, position: list, direction: float, speed: float):
        self.position = Point(*position)
        self.direction = direction
        self.speed = speed
        self.is_shooting = False
        self.is_alive = True

    def turn(self, direction: float, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot move")
        if (direction < 0 or direction > PI * 2):
            raise ValueError("'direction' should be between 0 and 2*pi")
            
        self.direction = direction


    def move(self, max_x: int, max_y: int, radius=0) -> bool:
        posx = self.position.x
        posy = self.position.y

        dest_x = self.position.x + cos(self.direction) * self.speed
        dest_y = self.position.y + sin(self.direction) * self.speed

        if dest_x - radius < 0:
            self.position.x = radius
        elif dest_x + radius > max_x:
            self.position.x = max_x - radius
        else:
            self.position.x = dest_x

        if dest_y - radius < 0:
            self.position.y = radius
        elif dest_y + radius > max_y:
            self.position.y = max_y - radius
        else:
            self.position.y = dest_y

        if posx == self.position.x and posy == self.position.y:
            logger.debug("Position unchanged")
            return False
        return True

    def set_is_moving(self, is_moving: bool, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player are already stopped")
            
        self.is_moving = is_moving


    def die(self, **kwargs) -> None:
        self.is_alive = False
        self.is_moving = False
        self.is_shooting = False


class Robot(Entity):
    size = 20
    def __init__(self, position: list):
        super().__init__(position, 0, ROBOT_SPEED)
        self.health = 10
        self.is_alive = True
        self.is_moving = False
        self.is_shooting = False
        
    def shoot(self, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot shoot")
            
        self.is_shooting = True
        
    def stop_shooting(self, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player has already stopped shooting")
            
        self.is_shooting = False

    def hit(self, **kwargs) -> None:
        if not self.is_alive:
            raise IsDead("Dead player cannot be hit again")
            
        self.health -= 1
        if self.health <= 0:
            self.die()

    def move(self, max_x, max_y, other_robots=None) -> bool:
        """              __
                        /  |< pos_right
              pos_left >|__/
                             | 
                          |NOT|    OK
                    OK     | OK| 
                            |  __
                              /  |< dest_right
                   dest_left >|__/"""

        if other_robots is None or len(other_robots) == 0:
            return super().move(max_x, max_y, self.size / 2)
        else:
            dest = Vector(self.direction, self.speed)(self.position)

            for other_robot in other_robots:
                rect = Rectangle(self.position, dest, self.size / 2)
                logger.debug("Quick position check %s in %s", other_robot.position, rect)
                if other_robot.position in rect:
                    logger.debug("Deep position check for same values")

                    # Compute a vector for my left and right hand
                    v_left = Vector(self.direction - PI / 4, self.size / 2)
                    v_right = Vector(self.direction + PI / 4, self.size / 2)

                    # Compute the two lines for my left and right hand to move to the destination
                    l_left = Line(v_left(self.position), v_left(dest))
                    l_right = Line(v_right(self.position), v_right(dest))

                    # Update the vectors to fit the size of the other robot
                    v_left.lenght = other_robot.size / 2
                    v_right.lenght = other_robot.size / 2

                    # Compute the left and right hand of the other robot
                    h_left = v_left(other_robot.position)
                    h_right = v_right(other_robot.position)

                    # Block if one of the hand of the other robot is in the "corridor" between l_left and l_right
                    if not ((l_left < h_left and l_left < h_right and l_right < h_left and l_right < h_right) or (
                             l_left > h_left and l_left > h_right and l_right > h_left and l_right > h_right)):
                        logger.debug("Blocked by %s", repr(other_robot.position))
                        return False

            # If not blocked: move
            return super().move(max_x, max_y, self.size / 2)


class Bullet(Entity):
    size = 2
    def __init__(self, shooter: Robot):
        super().__init__(shooter.position, shooter.direction, BULLET_SPEED)
        self.wall_hit = 0

    def turn(self, *args, **kwargs):
        pass

    def hit_wall(self, sizex: int, sizey: int) -> None:
        self.wall_hit += 1
        if (self.position.x <= 0 or self.position.x >= sizex):
            self.direction -= 2 * (self.direction - PI / 2)

        elif (self.position.y <= 0 or self.position.y >= sizey):
            self.direction = -self.direction

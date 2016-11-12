import random
from itertools import count
import logging
import math

logger = logging.getLogger(__name__)

try:
    from game_server.games.robotwar.settings import *
    from game_server.games.robotwar.entities import *
except ImportError:
    from settings import *
    from entities import *
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


class Status:
    """Garde une trace de ce qu'il s'est passé durant un tour"""
    def __init__(self, tickno: int):
        self.didsmthhappen = False
        self.tickno = tickno

    def add_robot(self, robot_id: int, robot: Robot):
        self.didsmthhappen = True
        if "robot" not in self.__dict__:
            self.robot = {}

        self.robot[robot_id] = {
            "position": robot.position,
            "direction": robot.direction,
            "isAlive": robot.is_alive,
            "isShooting": robot.is_shooting,
            "isMoving": robot.is_moving
        }

    def add_hit(self, shooter_id: int, victim_id: int) -> None:
        self.didsmthhappen = True
        if "hits" not in self.__dict__:
            self.hits = []

        self.hits.append({
            "shooter_id": shooter_id,
            "victim_id": victim_id
        })

    def add_bullet(self, bullet: Bullet) -> None:
        self.didsmthhappen = True
        if "bullets" not in self.__dict__:
            self.bullets = {}

        self.bullets[id(bullet)] = {
            "position": bullet.position,
            "direction": bullet.position,
            "speed": bullet.speed,
            "isAlive": bullet.is_alive
        }


    def getdict(self) -> dict:
        return self.__dict__

class RobotWar:
    def __init__(self, gameid: int, players: list, sizex: int, sizey: int):
        """
        For a given number of players, we split the map like that:
        __________  _________ _________
        |1      2|  |1  2  3| |1 2 3 4|
        |        |  |       | |5 6 7 8|
        |        |  |4  5  6| |9 0 1 2|
        |3      4|  |7  8  9| |3 4 5 6|
        __________  _________ _________

        each ceil has a min(x) and max(x) (same for y)
        we select a random position within each ceil
        and each player is placed at a randomly chosen position
        """

        self.get_events = lambda: ["die", "move", "stop", "shoot", "stop_shooting"]

        self.gameid = gameid
        self.sizex = sizex
        self.sizey = sizey
        self.robots = {}
        self.tickno = count()

                
        length = math.ceil(math.sqrt(len(players)))
        surface = length ** 2
        
        ceils = []
        for ceil in range(surface):
            posx = random.randrange(int(sizex / length * (ceil % 3)) - Robot.size / 2, 
                                    int(sizex / length * (ceil % 3 + 1)) - Robot.size / 2)

            posy = random.randrange(int(sizey / length * (ceil // 3)) - Robot.size / 2, 
                                    int(sizey / length * (ceil // 3 + 1)) - Robot.size / 2)

            ceils.append([posx, posy])
                        
        for player in players:
            ceil = random.choice(ceils)
            ceils.remove(ceil)
            self.robots[player] = Robot(ceil)

    def get_startup_status(self) -> dict:
        d = {
            "size": [self.sizex, self.sizey],
            "robots": {},
            "robot_size": Robot.size
        }
        for robot in self.robots:
            d["robots"][robot] = {
                "position": robot.position,
                "direction": robot.direction,
                "health": robot.health
            }

        return d

    def run_event(self, robot_id: int, event: str, **kwargs) -> None:
        getattr(self.robots[robot_id], event)(**kwargs)

    def main(self) -> dict:
        status = Status(next(self.tickno))
        self.handle_robots(status)
        self.handle_bullets(status)
        self.check_gameover(status)
        return status.getdict()

    def handle_robots(self, status: Status) -> None:
        for robot_id, robot in self.robots.items():
            if robot.is_moving:
                if robot.move(self.sizex, self.sizey, [other_robot for other_robot in self.robots.values() if other_robot != robot]):
                    logger.debug("Game ID %d: Player ID %d moved to %s", self.gameid, robot_id, robot.position)
                else:
                    logger.debug("Game ID %d: Player ID %d could not move", self.gameid, robot_id)

    def handle_bullets(self, status: Status) -> None:
        pass

    def check_gameover(self, status: Status) -> None:
        pass

                        
if __name__ == "__main__":
    jeu = RobotWar(0, [50, 51, 52, 53], 1920, 1080)
    jeu.robots[50].position.x = 400
    jeu.robots[50].position.y = 450
    jeu.robots[51].position.x = 445
    jeu.robots[51].position.y = 445
    jeu.robots[50].direction = 0
    jeu.robots[50].is_moving = True

    for robot_id, robot in jeu.robots.items():
        logger.debug("Robot %d %s", robot_id, repr(robot.position))

    while True:
        toeval = input("> ")
        if toeval == "quit":
            break
        elif toeval != "":
            eval(toeval)

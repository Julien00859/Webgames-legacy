import random
from itertools import count
import logging
import math
from time import time

from game_server.games.robotwar.settings import *
from game_server.games.robotwar.entities import *

logger = logging.getLogger(__name__)



class Status:
    """Garde une trace de ce qu'il s'est passé durant un tour"""
    def __init__(self, tickno: int):
        self.didsmthhappen = False
        self.tickno = tickno

    def update_robots(self, robot_id: int, robot: Robot):
        self.didsmthhappen = True
        if "robots" not in self.__dict__:
            self.robots = {}

        self.robots[str(robot_id)] = {
            "position": [robot.position.x, robot.position.y],
            "direction": robot.direction,
            "size": robot.size,
            "isAlive": robot.is_alive,
            "isShooting": robot.is_shooting,
            "isMoving": robot.is_moving
        }

    def update_bullets(self, bullet: Bullet) -> None:
        self.didsmthhappen = True
        if "bullets" not in self.__dict__:
            self.bullets = {}

        self.bullets[str(id(bullet))] = {
            "position": [bullet.position.x, bullet.position.y],
            "direction": bullet.direction,
            "speed": bullet.speed,
            "isAlive": bullet.is_alive
        }

    def set_winner(self, robot_id: int) -> None:
        self.didsmthhappen = True
        self.winner = robot_id


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

        self.get_events = lambda: ["die", "event_shoot", "event_stop_shooting", "event_move", "event_stop_moving", "event_rotate"]

        self.gameid = gameid
        self.sizex = sizex
        self.sizey = sizey
        self.robots = {}
        self.tickno = count()
        self.bullets = []
        self.gameover = False

                
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
            "frequency": 20
        }
        for robot_id, robot in self.robots.items():
            d["robots"][str(robot_id)] = {
                "position": [robot.position.x, robot.position.y],
                "direction": robot.direction,
                "health": robot.health,
                "size": robot.size,
                "isMoving": robot.is_moving,
                "isShooting": robot.is_shooting,
                "isAlive": robot.is_alive
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
                if robot.move(self.sizex, self.sizey, [other_robot for other_robot in self.robots.values() if other_robot != robot]) > 0:
                    logger.debug("Game ID %d: Player ID %d moved to %s", self.gameid, robot_id, robot.position)
                    status.update_robots(robot_id, robot)

                else:
                    logger.debug("Game ID %d: Player ID %d could not move", self.gameid, robot_id)

            if robot.is_shooting:
                now = time()
                if robot.last_attack + robot.attack_speed > now:
                    robot.last_attack = now
                    self.bullets.append(Bullet(robot))

    def handle_bullets(self, status: Status) -> None:
        for bullet in self.bullets.copy():
            robot_hit = bullet.move()
            if not bullet.is_alive:
                self.bullets.remove(bullet)

            if robot_hit is not None:
                status.update_robots(robot_hit)

            status.update_bullets(bullet)

    def check_gameover(self, status: Status) -> None:
        robots_alive = [robot_id for robot_id, robot in self.robots.items() if robot.is_alive]
        if len(robots_alive) == 1:
            status.set_winner(robots_alive[0])
            self.gameover = True
        elif len(robots_alive) == 0:
            status.set_winner(None)
            self.gameover = True

    def kill(self, robot_id):
        self.robots[robot_id].die()

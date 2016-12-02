import random
from itertools import count
import logging
import math
from time import time
import json
from collections import Iterable

import game_server.interfaces
from game_server.games.robotwar.settings import *
from game_server.games.robotwar.entities import *
from game_server.games.robotwar.geometry import *

logger = logging.getLogger(__name__)


class Status(game_server.interfaces.Status):
    """Garde une trace de ce qu'il s'est passé durant un tour"""
    robots = {}
    bullets = {}
    battlefield = {}

    def __init__(self, tickno: int):
        self.tickno = tickno

    def set_battlefield_size(self, battlefield: RectRange) -> None:
        self.battlefield_size = {
            "x": battlefield.max.x,
            "y": battlefield.max.y
        }

    def update_robots(self, robot_id: int, robot: Robot):
        self.didsmthhappen = True

        self.robots[str(robot_id)] = {
            "position": [robot.position.x, robot.position.y],
            "direction": robot.direction,
            "turretAngle": robot.turret_angle,
            "size": robot.size,
            "isAlive": robot.is_alive,
            "isShooting": robot.is_shooting,
            "isMoving": robot.is_moving
        }

    def update_bullets(self, bullet: Bullet) -> None:
        self.didsmthhappen = True

        self.bullets[str(id(bullet))] = {
            "position": [bullet.position.x, bullet.position.y],
            "direction": bullet.direction,
            "speed": bullet.speed,
            "isAlive": bullet.is_alive
        }

    def set_winners(self, winners: list) -> None:
        self.didsmthhappen = True
        self.winners = winners


    def tojson(self) -> str:
        return json.dumps({key: value for key, value in self.__dict__.items() if key != "didsmthhappen"})

    def __str__(self) -> str:
        return "<robotwar.Status#{}>".format(self.tickno) 

class RobotWar(game_server.interfaces.Game):
    get_events = lambda _: ["die", "event_shoot", "event_stop_shooting", "event_move", "event_stop_moving", "event_rotate"]
    bullets = []
    battlefield = object()
    frequency = 20

    def __init__(self, gameid: int, players: list):
        self.gameid = gameid
        self.bullets = []
        for player_id in players:
            self.players[player_id] = object()

    def start(self, sizex: int, sizey: int) -> Status:
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

        tickno = next(self.tickgen)
        status = Status(tickno)

        self.battlefield = RectRange(Point(0, 0), Point(sizex, sizey))
        status.set_battlefield_size(self.battlefield)
                
        length = math.ceil(math.sqrt(len(self.players)))
        surface = length ** 2
        
        ceils = []
        for ceil in range(surface):
            spawnpoint = Point(random.randrange(int(sizex / length * (ceil % length)) - Robot.size / 2, 
                                                int(sizex / length * (ceil % length + 1)) - Robot.size / 2),
                               random.randrange(int(sizey / length * (ceil // length)) - Robot.size / 2, 
                                                int(sizey / length * (ceil // length + 1)) - Robot.size / 2))

            ceils.append(spawnpoint)
                        
        for player_id in self.players:
            ceil = random.choice(ceils)
            ceils.remove(ceil)
            self.players[player_id] = Robot(ceil)
            status.update_robots(self.players[player_id])

        return status

    def play(self, *args, **kwargs) -> Status:
        status = Status(next(self.tickgen))
        self.handle_robots(status)
        self.handle_bullets(status)
        self.check_gameover(status)
        return status

    def handle_robots(self, status: Status) -> None:
        for robot_id, robot in self.robots.items():
            if robot.is_moving:
                if robot.move(self.battlefield.max.x, self.battlefield.max.y, [other_robot for other_robot in self.robots.values() if other_robot != robot]) > 0:
                    logger.debug("Game ID %d: Player ID %d moved to %s", self.gameid, robot_id, robot.position)
                    status.update_robots(robot_id, robot)

                else:
                    logger.debug("Game ID %d: Player ID %d could not move", self.gameid, robot_id)

            if robot.is_shooting:
                now = time()
                if robot.last_attack + robot.attack_speed < now:
                    logger.info("pan")
                    robot.last_attack = now
                    self.bullets.append(Bullet(robot))
                    status.update_bullets(self.bullets[-1])

            if robot.turret_angle_updated:
                robot.turret_angle_updated = False
                status.update_robots(robot_id, robot)

    def handle_bullets(self, status: Status) -> None:
        for bullet in self.bullets.copy():
            robot_hit = bullet.move(self.battlefield.max.x, self.battlefield.max.y)
            if not bullet.is_alive:
                self.bullets.remove(bullet)

            if robot_hit is not None:
                status.update_robots(robot_hit)

            status.update_bullets(bullet)

    def check_gameover(self, status: Status) -> None:
        robots_alive = [robot_id for robot_id, robot in self.robots.items() if robot.is_alive]
        if len(robots_alive) <= 1:
            status.set_winner(robots_alive)
            self.is_over = True

    def run_event(self, robot_id: int, event: str, **kwargs) -> None:
        getattr(self.robots[robot_id], event)(**kwargs)

    def kill(self, robot_id):
        self.robots[robot_id].die()

    def __str__(self) -> str:
        return "<robotwar.RobotWar#{}".format(self.gameid)

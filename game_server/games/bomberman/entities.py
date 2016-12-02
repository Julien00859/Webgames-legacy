from game_server.games.bomberman.settings import *
from collections import deque

class Entity:
    def __init__(self, pos, speed):
        self.position = pos
        self.offset = [GAME_OFFSET_PER_POSITION / 2, GAME_OFFSET_PER_POSITION / 2]
        self.direction = "S"
        self.speed = speed
        self.ismoving = False
        self.isalive = True

    def move(self, direction, *args, **kwargs):
        if self.isalive and direction in VECTORS:
            self.ismoving = True
            self.direction = direction

    def stop(self, *args, **kwargs):
        self.ismoving = False

    def die(self, *args, **kwargs):
        self.isalive = False
        self.ismoving = False

    def __str__(self):
        return "<Entity>"


class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, PLAYER_SPEED)
        self.power = PLAYER_POWER
        self.bomb = PLAYER_BOMB
        self.has_mine = PLAYER_START_WITH_MINE
        self.has_hammer = PLAYER_START_WITH_HAMMER

        self.plant_event = False
        self.fuse_event = False

        self.mines = deque()

    def plant(self, *args, **kwargs):
        self.plant_event = True

    def fuse(self, *args, **kwargs):
        self.fuse_event = True

    def __str__(self):
        return "<Player>"


class Bomb(Entity):
    def __init__(self, master):
        super().__init__(master.position.copy(), BOMB_SPEED)
        self.master = master
        self.power = master.power
        self.fuse_time = BOMB_FUSE_TIME
        self.exploded = False

    def countdown(self):
        if not self.exploded:
            if self.fuse_time > 0:
                self.fuse_time -= 1
            else:
                self.explose()

    def explose(self):
        if not self.exploded:
            self.exploded = True
            self.master.bomb += 1
            self.die()

    def __str__(self):
        return "<Bomb>"


class Mine(Bomb):
    def __init__(self, master):
        super().__init__(master)

    def countdown(self):
        pass

    def __str__(self):
        return "<Mine>"

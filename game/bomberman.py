from collections import deque, defaultdict
from game.entities import *
from itertools import starmap
from operator import itemgetter, add
from os.path import join as pathjoin
from random import random, choice
from settings.game_settings import *
import logging

logger = logging.getLogger(__name__)

def zip_list(*iterables):
    """ zip() -> [(), ()]
        zip_list() -> [[], []]"""

    sentinel = object()
    iterators = [iter(it) for it in iterables]
    while iterators:
        result = []
        for it in iterators:
            elem = next(it, sentinel)
            if elem is sentinel:
                return
            result.append(elem)
        yield list(result)


def updatable_queue(iterable):
    """Because I need a queue list that can be updated on iteration"""
    dq = deque(iterable)
    while dq:
        new = yield dq.pop(0)
        while new is not None:
            dq.append(new)
            new = yield


class Status:
    """Garde une trace de ce qu'il s'est passé durant un tour"""
    def __init__(self, tickno):
        self.didsmthhappen = False
        self.tickno = tickno

    def add_entity(self, entity, id_=None):
        self.didsmthhappen = True
        if "entities" not in self.__dict__:
            self.entities = dict()

        self.entities[id(entity) if id_ is None else id_] = {
            "name": str(entity),
            "isalive": entity.isalive,
            # player.postition + (player.offset / offset_per_position)
            "position": list(starmap(add, zip(entity.position, map(lambda x: x / GAME_OFFSET_PER_POSITION, entity.offset)))),
            "ismoving": entity.ismoving
        }

    def add_explosion(self, bomb):
        self.didsmthhappen = True
        if "explosions" not in self.__dict__:
            self.explosions = dict()

        self.explosions[id(bomb)] = {
            "name": str(bomb),
            "position": bomb.position,
            "radius": bomb.power
        }

    def update_map(self, xpos, ypos, ceil):
        self.didsmthhappen = True
        if "map" not in self.__dict__:
            self.map = dict()

        # In python you can use anything hashable as dictionnary key.
        # In javascript it has to be a string
        # str([]) is an hack to convert a python's list into a JSON list
        self.map[str([xpos, ypos])] = ceil

    def gameover(self, winner=None):
        self.didsmthhappen = True
        self.winner = winner

    def get_dict(self):
        return self.__dict__


class Bomberman:
    """Le jeu"""

    def __init__(self, gameid: int, players: list, mapname: str):
        """Initialise avec un nom de map et des joueurs"""

        # Ouvre le fichier map et fait correspondre la ligne à l'axe des ordonnées
        # et l'index dans une ligne à l'axe des absises (pour avoir self.map[x][y] comme en math)
        with open(pathjoin("game", "maps", mapname), "r") as mapfile:
            self.map = list(zip_list(*[list(line) for line in mapfile.readlines()]))

        self.players = {}
        for xpos, row in enumerate(self.map):
            for ypos, ceil in enumerate(row):
                # Pour chaque case
                # Si c'est un brique, il y a un peu de chance d'être changé en vide
                if ceil == MAP_BRICK:
                    if random() < MAP_BRICK_TO_VOID_RATIO:
                        ceil = MAP_VOID
                # Si c'est un nombre, on lui associe un joueur (si il en reste)
                elif ceil.isdigit():
                    if int(ceil) < len(players):
                        self.players[players[int(ceil)]] = Player([xpos, ypos])
                    self.map[xpos][ypos] = MAP_VOID

        if len(self.players.keys()) < len(players):
            raise ValueError("Impossible to spawn all players")

        self.gid = gameid
        self.bombs = []
        self.gameover = False
        self.tickno = 0

    def get_startup_status(self):
        return {
            "map": self.map,
            "players": {
                player: {
                    "position": list(starmap(add, zip(self.players[player].position, map(lambda x: x / GAME_OFFSET_PER_POSITION, self.players[player].offset)))),
                    "direction": self.players[player].direction
                } for player in self.players
            }
        }

    def handle_players(self, status):
        """Fonction de gestion des joueurs."""

        # Pour chaque joueur
        for pid, player in self.players.items():
            # Calcule le déplacement du joueur et met à jour le statut
            if player.ismoving:
                oldpos = list(starmap(add, zip(player.position, map(lambda x: x / GAME_OFFSET_PER_POSITION, player.offset))))
                if self.move_entity(player, status):
                    newpos = list(starmap(add, zip(player.position, map(lambda x: x / GAME_OFFSET_PER_POSITION, player.offset))))
                    if (oldpos == newpos):
                        logger.warning("Game ID %d: Internal Error, player ID %d didn't move but still moving.", self.gid, pid)
                        player.stop()
                    else:
                        logger.debug("Game ID %d: Player ID %d moved from %s to %s", self.gid, pid, oldpos, newpos)
                        status.add_entity(player, pid)

            # Gère l'événement "poser une bombe" et met à jour le statut
            if player.plant_event and player.bomb > 0:
                player.plant_event = False
                player.bomb -= 1

                # Le joueur pose une mine
                if player.has_mine:
                    b = Mine(player)
                    player.mines.append(b)
                    self.bombs.append(b)
                    self.map[m.position[0]][m.position[1]] = MAP_MINE
                    status.add_entity(b)
                    logger.debug("Game ID %d: Player ID %d planted a %s at %s", self.gid, pid, repr(m), m.position)

                # Le joueur pose une bombe
                else:
                    b = Bomb(player)
                    self.bombs.append(b)
                    self.map[m.position[0]][m.position[1]] = MAP_BOMB
                    status.add_entity(b)
                    logger.debug("Game ID %d: Player ID %d planted a %s at %s", self.gid, pid, repr(b), b.position)

            # Gère l'événement "actionner une mine"
            if player.fuse_event and player.has_mine:
                player.fuse_event = False
                if self.player.mines:
                    m = self.player.mines.popleft()
                    m.explose()
                    logger.debug("Game ID %d: Player ID %d fused a %s at %s", self.gid, pid, repr(b), b.position)

    def handle_powerup(self, entity, status):
        """Fonction qui récupère la position d'une entité pour vérifier s'il y a un powerup à la même position
        Si l'entité est un joueur, le powerup s'applique, sinon le powerup est détruit"""
        ceil = self.map[entity.position[0]][entity.position[1]]
        if ceil in map((itemgetter(0)), POWERUPS):
            if isinstance(entity, Player):
                logger.debug("Game ID %d: Player ID %d got powerup %s at %s", self.gid, [pid for (pid, player) in self.players if player == entity][0], ceil, entity.position)
                if ceil == MAP_POWERUP_BOMB:
                    entity.bomb += 1
                elif ceil == MAP_POWERUP_MINE:
                    entity.has_mine = True
                elif ceil == MAP_POWERUP_POWER:
                    entity.power += 1
                elif ceil == MAP_POWERUP_SPEED:
                    entity.speed += int(PLAYER_SPEED / 5)
                elif ceil == MAP_POWERUP_HAMMER:
                    entity.has_hammer = True

            else:
                logger.debug("Game ID %d: powerup %s at %s has been destroy", self.gid, ceil, entity.position)
            self.map[entity.position[0]][entity.position[1]] = MAP_VOID
            status.update_map(xpos, ypos, MAP_VOID)

    def handle_bombs(self, status):
        """Fonction de gestion des bombes et des mines"""

        udq = updatable_queue(self.bombs)

        # Pour chaque bombe
        for bomb in udq:
            # Décrémente leur compte-à-rebourt
            bomb.countdown()

            # Dans le cas d'une explosion
            if bomb.exploded:

                # Met à jour le status, la carte et la liste des bombes
                status.add_explosion(bomb)
                self.map[bomb.position[0]][bomb.position[1]] = MAP_VOID
                self.bombs.remove(bomb)
                logger.debug("Game ID %d: Bomb ID %d exploded at %s", self.gid, id(bomb), bomb.position)

                # Calcule la déflagration
                for vector in VECTORS:
                    for radius in range(bomb.power + 1):
                        xpos = bomb.position[0] + vector[0] * radius
                        ypos = bomb.position[1] + vector[1] * radius

                        # Si une bombe est sur la déflagration, celle-ci explose
                        b = get_bomb_at_pos(xpos, ypos)
                        if b is not None:
                            b.explose()

                            # Afin de calculer également la déflagration de cette bombe durant ce tour
                            # On s'assure que la bombe soufflée soit à la suite de la bombe actuelle
                            if self.bombs.index(b) < self.bombs.index(bomb):
                                self.bombs.remove(b)
                                udq.send(b)

                        # Si un joueur est sur la déflagration, celui-ci meurt
                        pid, p = get_player_at_pos(xpos, ypos)
                        if p is not None:
                            p.die()
                            status.add_entity(p, pid)
                            logger.debug("Game ID %d: Bomb ID %d blew Player ID %d at %s", self.gid, id(bomb), pid, p.position)

                        # Si la déflagration touche un mur, elle s'arrête
                        if self.map[xpos][ypos] == MAP_WALL:
                            break

                        # Sinon si c'est une brique, la brique peut devenir un powerup, le status est mis à jour et la déflagration s'arrête
                        elif self.map[xpos][ypos] == MAP_BRICK:
                            if random() > MAP_BRICK_to_powerup_ratio:
                                powerup = choices([pwup for pwup, weigth in POWERUPS for i in range(weigth)])
                                self.map[xpos][ypos] = powerup
                                status.update_map(xpos, ypos, powerup)
                                logger.debug("Game ID %d: Bomb ID %d blew a brick to a powerup \"%s\" at [%d, %d]", self.gid, id(bomb), powerup, xpos, ypos)
                            break

                        # Sinon si c'est un powerup, il est soufflé, le status est mis à jour et la déflagration s'arrête
                        elif self.map[xpos][ypos] in map((itemgetter(0)), POWERUPS):
                            self.map[xpos][ypos] = MAP_VOID
                            status.update_map(xpos, ypos, MAP_VOID)
                            logger.debug("Game ID %d: Bomb ID %d blew a powerup \"%s\" at [%d, %d]", self.gid, id(bomb), powerup, xpos, ypos)
                            break

            # Calcule le décplacement et met à jour le statut
            if bomb.ismoving:
                oldpos = list(starmap(add, zip(bomb.position, map(lambda x: x / GAME_OFFSET_PER_POSITION, bomb.offset))))
                self.map[bomb.position[0]][bomb.position[1]] = MAP_VOID
                if self.move_entity(bomb, status):
                    status.add_entity(bomb)
                    newpos = list(starmap(add, zip(bomb.position, map(lambda x: x / GAME_OFFSET_PER_POSITION, bomb.offset))))
                    logger.debug("Game ID %d: Player ID %d moved from %s to %s", self.gid, pid, oldpos, newpos)

                if isinstance(bomb, Bomb):
                    self.map[bomb.position[0]][bomb.position[1]] = MAP_BOMB
                elif isinstance(bomb, Mine):
                    self.map[bomb.position[0]][bomb.position[1]] = MAP_MINE

    def main(self):
        """Fonction de gestion d'un tick du jeu, promet de compléter un statut qui récapitulera le déroulement de ce tick"""
        if not self.gameover:
            self.tickno += 1
            status = Status(self.tickno)
            self.handle_players(status)
            self.handle_bombs(status)
            self.check_gameover(status)
            return status.get_dict()

    def iswalkable(self, xpos: int, ypos: int):
        """Fonction qui retourne vrai si un joueur peut marcher sur la case désigné"""
        return self.map[xpos][ypos] not in [MAP_WALL, MAP_BRICK, MAP_BOMB, MAP_MINE]

    def get_bomb_at_pos(self, xpos: int, ypos: int):
        """Retourne qui retourne la bombe à la case spécifié ou None"""
        for bomb in self.bombs:
            if bomb.position == (xpos, ypos):
                return bomb
        else:
            return None

    def get_player_at_pos(self, xpos: int, ypos: int):
        """Retourne qui retourne le joueur à la case spécifié ou None"""
        for playerid, player in self.players.items():
            if player.position == (xpos, ypos):
                return playerid, player
        else:
            return None, None

    def move_entity(self, entity: Entity, status: Status):
        """Fonction gérant le déplacement des entitées, retourne vrai si la position de l'entité a changé, faux dans les autres cas"""

        # L'histoire du schémas qui explique tout

        # 0xxxxxxxxxx1xxxxxxxxxx2
        # x##########|##########|
        # x##########|##########|
        # x##########|##########|
        # x###       |          |
        # x###    x+1>       x+1<
        # x###       <x-1       >
        # x###       |          |
        # x###    ###|###    ###|           "x": Le joueur ne peut pas se déplacer vers la case juxtaposée
        # x###    ###|###    ###|
        # x### y+1###|### y+1###|
        # 1---/\/----+---/\/----+           "|", "-": Le joueur peut se déplacer vers la case juxtaposée
        # x###y-1 ###|###y-1 ###|
        # x###    ###|###    ###|
        # x###    ###|###    ###|           "#": Le joueur ne peut pas se déplacer à cet endroit pour des questions de rendu graphique.
        # x###       |          |
        # x###    x+1>          <
        # x###       <x-1    x+1>
        # x###       |          |
        # x###    ###|###    ###|
        # x###    ###|###    ###|
        # x### y+1###|### y+1###|
        # 2---/\/----+---/\/----+

        # Récupère les coordonnées de la case vers laquelle le joueur se dirige
        xpos, ypos = starmap(add, zip(entity.position, VECTORS[entity.direction]))

        # Si il peut marcher dessus
        if self.iswalkable(xpos, ypos):

            # Le joueur se déplace sur l'axe des absises
            if entity.direction in ["W", "E"]:
                # On calcule son déplacement
                xoff = entity.offset[0] + VECTORS[entity.direction][0] * entity.speed

                # Ceci vérifie que le joueur se déplace toujours autours du milieu de son axe (pas sur les #)
                if GAME_OFFSET_PER_POSITION / 4 < entity.offset[1] < GAME_OFFSET_PER_POSITION / 4 * 3:
                    entity.offset[0] = xoff
                else:
                    if xoff < GAME_OFFSET_PER_POSITION / 4:
                        entity.offset[0] = GAME_OFFSET_PER_POSITION / 4
                        return False
                    elif xoff > GAME_OFFSET_PER_POSITION / 4 * 3:
                        entity.offset[0] = GAME_OFFSET_PER_POSITION / 4 * 3
                        return False
                    else:
                        entity.offset[0] = xoff

            # Le joueur se déplace sur l'axe des ordonnées
            else:
                # On calcule son déplacement
                yoff = entity.offset[1] + VECTORS[entity.direction][1] * entity.speed

                # Ceci vérifie que le joueur se déplace toujours autours du milieu de son axe (pas sur les #)
                if GAME_OFFSET_PER_POSITION / 4 < entity.offset[0] < GAME_OFFSET_PER_POSITION / 4 * 3:
                    entity.offset[1] = yoff
                else:
                    if yoff < GAME_OFFSET_PER_POSITION / 4:
                        entity.offset[1] = GAME_OFFSET_PER_POSITION / 4
                        return False
                    elif yoff > GAME_OFFSET_PER_POSITION / 4 * 3:
                        entity.offset[1] = GAME_OFFSET_PER_POSITION / 4 * 3
                        return False
                    else:
                        entity.offset[1] = yoff

            # Lorsque l'offset excède ou décède le nombre d'unité par case, on met à jour la position
            if entity.offset[0] < 0:
                entity.position[0] -= 1
                entity.offset[0] += GAME_OFFSET_PER_POSITION

            elif entity.offset[0] > GAME_OFFSET_PER_POSITION:
                entity.position[0] += 1
                entity.offset[0] -= GAME_OFFSET_PER_POSITION

            elif entity.offset[1] < 0:
                entity.position[1] -= 1
                entity.offset[1] += GAME_OFFSET_PER_POSITION

            elif entity.offset[1] > GAME_OFFSET_PER_POSITION:
                entity.position[1] += 1
                entity.offset[1] -= GAME_OFFSET_PER_POSITION

            else:
                return True  # It's a hack to not check wether we walk to a powerup

            self.handle_powerup(entity, status)

        # Le joueur ne peut pas se diriger sur la case voulu (question de position),
        # on regarde s'il peut tout de même se rapprocher du mur
        elif entity.direction == "N" and entity.offset[1] > GAME_OFFSET_PER_POSITION / 4:
            off = entity.offset[1] + VECTORS[entity.direction][1] * entity.speed
            if off > GAME_OFFSET_PER_POSITION / 4:
                entity.offset[1] = off
            else:
                entity.offset[1] = GAME_OFFSET_PER_POSITION / 4
                entity.stop()
                return False

        elif entity.direction == "S" and entity.offset[1] < GAME_OFFSET_PER_POSITION / 4 * 3:
            off = entity.offset[1] + VECTORS[entity.direction][1] * entity.speed
            if off < GAME_OFFSET_PER_POSITION / 4 * 3:
                entity.offset[1] = off
            else:
                entity.offset[1] = GAME_OFFSET_PER_POSITION / 4 * 3
                entity.stop()
                return False

        elif entity.direction == "W" and entity.offset[0] > GAME_OFFSET_PER_POSITION / 4:
            off = entity.offset[0] + VECTORS[entity.direction][1] * entity.speed
            if off > GAME_OFFSET_PER_POSITION / 4:
                entity.offset[0] = off
            else:
                entity.offset[0] = GAME_OFFSET_PER_POSITION / 4
                entity.stop()
                return False

        elif entity.direction == "E" and entity.offset[0] < GAME_OFFSET_PER_POSITION / 4 * 3:
            off = entity.offset[0] + VECTORS[entity.direction][1] * entity.speed
            if off < GAME_OFFSET_PER_POSITION / 4 * 3:
                entity.offset[0] = off
            else:
                entity.offset[0] = GAME_OFFSET_PER_POSITION / 4 * 3
                entity.stop()
                return False

        # L'entité n'a pas pu se déplacer
        else:
            entity.stop()
            return False

        # L'entité a pu se déplacer
        return True

    def kill(self, player):
        """Tue le joueur spécifié"""
        self.players[player].die()

    def check_gameover(self, status):
        """Vérifie si la partie est finie et met à jour le statut si c'est le cas"""
        alives = [pid for pid, player in self.players.items() if player.isalive]
        if len(alives) <= 1:
            self.gameover = True
            status.gameover(alives[0] if alives else None)

    def run_event(self, pid, event, **kwargs):
        getattr(self.players[pid], event)(**kwargs)

    def get_events(self):
        return [attr for attr in dir(Player) if not attr.startswith("__")]

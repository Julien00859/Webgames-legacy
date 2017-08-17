"""Use docker to start games"""

from collections import deque, namedtuple
from datetime import datetime
from functools import partial
from logging import getLogger
from random import shuffle
from uuid import uuid4
import asyncio

import jwt

from config import JWT_EXPIRATION_TIME, JWT_SECRET, API_URL, READY_CHECK_TIMEOUT
from tools import asyncpartial, run_redis_script, udpbroadcaster_send
import shared

logger = getLogger(__name__)
ports = deque(range(45000, 46000))
shuffle(ports)
class Game:
    def __init__(self, info, rcff, players):
        self.name = info.name
        self.ports = info.ports
        self.threshold = info.threshold
        self.ready_check_fail_future = rcff
        self.players = players
        self.readycnt = 0

def ready_check(game_info, players_ids):
    game_id = uuid4()
    logger.info("Init new %s with id %s", game_info.name, game_id)
    asyncio.ensure_future(shared.redis.sadd(f"games:{game_id}:players", *players_ids))
    future = asyncio.get_event_loop().call_later(READY_CHECK_TIMEOUT, ready_check_fail, game_id)
    shared.games[game_id] = Game(game_info, future, players_ids)
    getLogger(f"{__name__}.{game_id}").info("Send ready check challenge to users")
    udpbroadcaster_send("readycheck", players_ids, game_info.name, game_id)

def ready_check_fail(game_id):
    getLogger(f"{__name__}.{game_id}").info("Ready check challenge failed")
    asyncio.ensure_future(run_redis_script("remove_game.lua", [str(game_id), str(len(shared.games[game_id].players))], []))
    del shared.games[game_id]
    udpbroadcaster_send("readyfail", game_id)

async def run(game_id):
    game = shared.games[game_id]
    glogger = getLogger(f"{__name__}.{game_id}")
    glogger.info("Ready check challenge successful !")
    relay_to_players = partial(udpbroadcaster_send, "relay_to_players", game.players)

    glogger.debug("Generate JSON Web Token")
    gjwt = jwt.encode({
        "iss": "manager",
        "sub": "webgames",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + JWT_EXPIRATION_TIME,
        "type": "game",
        "id": str(game_id),
        "name": game.name
    }, JWT_SECRET)

    glogger.debug("Register in Web API")
    await shared.http.post(f"{API_URL}/games", json={
        "name": game.name,
        "id": str(game_id),
        "players": game.players
    })

    myports = [ports.pop() for n in range(len(game.ports))]
    myports_str = " ".join([game.ports[n][1] + ":" + str(myports[n]) for n in range(len(myports))])

    relay_to_players(f"gamestart {game.name} {game_id} {myports_str}")

    glogger.info("Start game")
    await asyncio.sleep(10)
    glogger.info("Stop game")

    await run_redis_script("remove_game.lua", [str(game_id), len(game.players)], [])

    await shared.http.delete(f"{API_URL}/games/{game_id}")
    relay_to_players(f"gameover {game.name} {game_id}")

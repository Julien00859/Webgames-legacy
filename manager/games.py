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
Game = namedtuple("Game", ["info", "ready_check_fail_future", "players", "areready"])

def ready_check(game, players_ids):
    loop = asyncio.get_event_loop()
    game_id = str(uuid4())
    glogger = getLogger(f"{__name__}.{game_id}")
    logger.info("Init new %s with id %s", game.name, game_id)
    asyncio.ensure_future(shared.redis.sadd(f"games:{game_id}:players", *players_ids))
    future = loop.call_later(READY_CHECK_TIMEOUT, ready_check_fail, game_id)
    shared.games[game_id] = Game(game, future, players_ids, 0)
    logger.info("Send ready check challenge to users")
    udpbroadcaster_send("ready_check", players_ids, game.name, game_id)

def ready_check_fail(game_id):
    glogger = getLogger(f"{__name__}.{game_id}")
    glogger.info("Ready check challenge failed")
    asyncio.ensure_future(run_redis_script("remove_game.lua", [game_id, str(len(shared.games[game_id].players))], []))
    del shared.games[game_id]
    udpbroadcaster_send("ready_check_fail", game_id)

async def run(game_id):
    glogger = getLogger(f"{__name__}.{game_id}")
    glogger.info("Ready check challenge successful !")
    game = shared.games[game_id].info
    players_ids = shared.games[game_id].players

    await shared.redis.rpush("games:" + gid + ":players", *players_ids)
    relay_to_players = partial(udpbroadcaster_send, "relay_to_players", players_ids)

    glogger.debug("Generate JSON Web Token")
    gjwt = jwt.encode({
        "iss": "manager",
        "sub": "webgames",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + JWT_EXPIRATION_TIME,
        "type": "game",
        "id": gid,
        "name": game.name
    }, JWT_SECRET)

    glogger.debug("Register in Web API")
    await shared.http.post(f"{API_URL}/games", json={
        "name": game.name,
        "id": gid,
        "players": players_ids
    })

    myports = [ports.pop() for n in range(len(game.ports))]
    myports_str = " ".join([game.ports[n][1] + ":" + str(myports[n]) for n in range(len(myports))])

    relay_to_players(f"gamestart {game.name} {gid} {myports_str}")

    glogger.info("Start game")
    await asyncio.sleep(2)
    glogger.info("Stop game")

    await run_redis_script("remove_game.lua", [game_id, len(shared.games[game_id].players)])

    await shared.http.delete(f"{API_URL}/games/{gid}")
    relay_to_players(f"gameover {game.name} {gid}")

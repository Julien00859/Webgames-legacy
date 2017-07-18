"""Use docker to start games"""

from collections import deque
from datetime import datetime
from functools import partial
from logging import getLogger
from random import shuffle
from uuid import uuid4

import asyncio
import jwt

from config import JWT_EXPIRATION_TIME, JWT_SECRET, API_URL
from tools import asyncpartial, run_redis_script
import shared

logger = getLogger(__name__)
ports = deque(range(45000, 46000))
shuffle(ports)

async def run(game, players_ids):
    gid = str(uuid4())
    glogger = getLogger("{}.{}.{}".format(__name__, game.name, gid))
    logger.info("Init new %s with id %s", game.name, gid)
    await shared.redis.rpush("games:" + gid + ":players", *players_ids)

    glogger.debug("Getting players...")
    my_players = []
    their_players = []
    for client in shared.clients:
        if not client.closed \
           and client.jwtdata is not None \
           and client.jwtdata.type == "user":
            if client.jwtdata.id in players_ids:
                glogger.debug("Found %s", str(client))
                my_players.append(client)
            else:
                glogger.debug("Skip %s", str(client))
                their_players.append(client)
    send_to_all_ = asyncpartial(send_to_all, my_players, their_players)

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
    await shared.http.post(API_URL + "/games", json={
        "name": game.name,
        "id": gid,
        "players": players_ids
    })

    global ports
    myports = [ports.pop() for n in range(len(game.ports))]
    myports_str = " ".join([game.ports[n][1] + ":" + str(myports[n]) for n in range(len(myports))])

    await send_to_all_("gamestart {} {} {}".format(game.name, gid, myports_str))

    glogger.info("Start game")
    await asyncio.sleep(2)
    glogger.info("Stop game")

    await shared.redis.delete("games:" + gid + ":players")
    await run_redis_script("remove_player_from_queues.lua", players_ids, shared.queues)

    await send_to_all_("gameover {} {}".format(game.name, gid))

async def send_to_all(my_players, their_players, message):
    for player in my_players:
        if not player.closed:
            await player.send(message)

    # Message Queue

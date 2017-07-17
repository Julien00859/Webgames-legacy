from config import *
from collections import deque
from random import shuffle
from logging import getLogger
import shared
import asyncio
from tools import *
from uuid import uuid4
import jwt
from datetime import datetime
from functools import partial

logger = getLogger(__name__)
ports = deque(range(45000, 46000))
shuffle(ports)

async def run(game, players_ids):
    gid = str(uuid4())
    glogger = getLogger("{}.{}.{}".format(__name__, game.name, gid))
    logger.info("Init new %s with id %s", game.name, gid)
    await shared.redis.rpush("games:" + gid + ":players", *players_ids)

    glogger.debug("Get players")
    my_players = []
    their_players = []
    for client in shared.clients:
        if not client.closed \
           and client.jwtdata is not None \
           and client.jwtdata.type == "user":
            if client.jwtdata.id in players_ids:
                logger.debug("Found %s", str(client))
                my_players.append(client)
            else:
                logger.debug("Skip %s", str(client))
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
    for pid in players_ids:
        await run_redis_script("remove_player.lua", [pid], shared.queues)
    
    await send_to_all_("gameover {} {}".format(game.name, gid))

async def send_to_all(my_players, their_players, message):
    for player in my_players:
        if not player.closed:
            await player.send(message)
    
    # Message Queue
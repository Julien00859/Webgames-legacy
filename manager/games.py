from config import *
from collections import deque
from random import shuffle
from logging import getLogger
from shared import *

logger = getLogger(__name__)
ports = deque(range(45000, 46000))
shuffle(ports)

games = {}

async def run(game, playersid):
    gid = str(uuid4())
    glogger = getLogger(__name__ + "." + gid)
    logger.info("Init new %s with id %s", game.name, gid)

    logger.debug("Get players")
    players = []
    for client in clients:
        if not client.closed \
           and client.type == "user" \
           and client.id is not None \
           and client.id in players:
            players.append(client)

    logger.debug("Generate JSON Web Token")
    gjwt = jwt.encode({
        "iss": "manager",
        "sub": "webgames",
        "iat": datetime.utcnow(), 
        "exp": datetime.utcnow() + JWT_EXPIRATION_TIME,
        "type": "game",
        "id": gid,
        "name": game.name
    }, JWT_SECRET)

    logger.debug("Register game in API")
    http.post(API_URL + "/games", json={
        "name": game.name,
        "id": gid,
        "players": players
    })

    logger.debug("Start game")
    # TODO
    # lancer le container

    logger.debug("Invite players")
    for player in players:
        player.queue = None
        player.gameid = gid
        await player.send("gamestart")

    # TODO
    # afficher les logs

    logger.info("Stopping...")
    # TODO
    # lorsque le jeu s'arrête

    logger.debug("Free players")
    for player in players:
        player.gameid = None
        await player.send("gameover")

    

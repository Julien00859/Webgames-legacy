from clients_handler import ClientHandler
from server import redis, http
from config import *

def start(game, players):
    jwt_data = {
        "iss": "manager",
        "sub": "webgames",
        "iat": datetime.utcnow(), 
        "exp": datetime.utcnow() + JWT_EXPIRATION_TIME,
        "type": "game",
        "id": uuid4(),
        "name": game.name
    }

    redis.sadd("game:%s:players" % jwt_data["id"], *players)

    http.post(API_URL + "/games", json={
        "name": game.name
        "id": jwt_data["id"],
        "players": players
    })

    # send ID on RabbitMQ

    for client in ClientHandler.clients:
        if client.jwt is not None \
           and client.jwt["type"] == "user" \
           and client.jwt["id"] in players:
            client.send("gamestart")

    # lancer le container

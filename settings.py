from os import listdir, environ
from os.path import join as pathjoin
from random import choice

import game_server.games.bomberman.bomberman
import game_server.games.robotwar.robotwar

# OS
CHROOT_TO_PROJECT_DIR = False # Only available on Linux


# Auth Server
START_AUTH_SERVER = False
if START_AUTH_SERVER:
    AUTH_HOST = "localhost"
    AUTH_PORT = 28457
    SSL_KEY_PATH = environ["WG_KEYPATH"] 
    SSL_CERT_PATH = environ["WG_CERTPATH"]
    TOKEN_LENGTH = 16


# Game Server
START_GAME_SERVER = True
if START_GAME_SERVER:

    # TCP Server
    LISTEN_ON_TCP = True
    if LISTEN_ON_TCP:
        TCP_HOST = "localhost"
        TCP_PORT = 28458

    # WebSocket Server
    LISTEN_ON_WEBSOCKET = True
    if LISTEN_ON_WEBSOCKET:
        WS_HOST = "localhost"
        WS_PORT = 28459

    # Game Manager
    GAME_FREQUENCY = 20
    PLAYERS_PER_GAME = 2
    GAMES = {
        "bomberman": {
            "gamefunc": game_server.games.bomberman.bomberman.Bomberman,
            "startfunc": (lambda: {"mapname": choice(listdir(pathjoin("game_server", "games", "bomberman", "maps")))})
        },
        "robotwar": {
        	"gamefunc": game_server.games.robotwar.robotwar.RobotWar,
        	"startfunc": (lambda: {"sizex": 1500, "sizey": 700})
        }
    }


# Database
DB_URI = environ["WG_DATABASE"]


# Log
LOG_TO_CONSOLE = True
LOG_CONSOLE_LEVEL = "INFO"

LOG_TO_FILE = True
KEEP_LOG = True
LOG_DIR = "logs"
LOG_FILE_NAME = "latest.log"
LOG_FILE_LEVEL = "INFO"

LOG_TO_DB = True
LOG_DB_LEVEL = "INFO"

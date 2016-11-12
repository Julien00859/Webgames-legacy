from os import listdir, environ
from os.path import join as pathjoin
from random import choice

import game_server.games.bomberman.bomberman
import game_server.games.robotwar.robotwar

# OS
CHROOT_TO_PROJECT_DIR = False # Only available on Linux

# Web Server
WS_HOST = "localhost"
WS_PORT = 28456

# Auth Server
AUTH_HOST = "localhost"
AUTH_PORT = 28457
SSL_KEY_PATH = environ["KEYPATH"] 
SSL_CERT_PATH = environ["CERTPATH"]
TOKEN_LENGTH = 16

# Game Manager
PLAYERS_PER_GAME = 2
GAMES = {
    "bomberman": {
        "gamefunc": game_server.games.bomberman.bomberman.Bomberman,
        "initfunc": (lambda: {"mapname": choice(listdir(pathjoin("game_server", "games", "bomberman", "maps")))})
    },
    "robotwar": {
    	"gamefun": game_server.games.robotwar.robotwar.RobotWar,
    	"initfunc": (lambda: {"sizex": 1920, "sizey": 1080})
    }
}

# Database
DB_URI = environ["DBURI"]

# Log
LOG_STDOUT = True
LOG_STDERR = False

LOG_TO_CONSOLE = True
LOG_CONSOLE_LEVEL = "INFO"

LOG_TO_FILE = True
KEEP_LOG = True
LOG_FILE_NAME = "latest.log"
LOG_FILE_LEVEL = "DEBUG"

LOG_TO_DB = True
LOG_DB_LEVEL = "DEBUG"

LOG_DIR = "logs"

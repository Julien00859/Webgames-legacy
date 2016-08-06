from os import listdir
from os.path import join as pathjoin
from random import choice

import game_server.games.bomberman.bomberman

# OS
CHROOT_TO_PROJECT_DIR = False # Only available on Linux

# Web Server
HOST = "0.0.0.0"
PORT = 28456

# Security
TOKEN_LENGTH = 16

# Game Manager
PLAYERS_PER_GAME = 2
GAMES = {
    "bomberman": {
        "gamefunc": game_server.games.bomberman.bomberman.Bomberman,
        "initfunc": (lambda: {"mapname": choice(listdir(pathjoin("game_server", "games", "bomberman", "maps")))})
    }
}

# Log
LOG_CONSOLE_LEVEL = "INFO"

LOG_TO_FILE = True
KEEP_LOG = False
LOG_FILE_NAME = "latest.log"
LOG_FILE_LEVEL = "DEBUG"


LOG_TO_DB = True
LOG_DB_NAME = "log.db"
LOG_DB_LEVEL = "DEBUG"

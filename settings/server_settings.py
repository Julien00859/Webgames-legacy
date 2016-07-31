from game.bomberman import Bomberman
from os import listdir
from random import choice
from os.path import join as pathjoin

# OS
CHROOT_TO_PROJECT_DIR = True # Only available on Linux

# Web Server
HOST = "0.0.0.0"
PORT = 28456

# Security
TOKEN_LENGTH = 16

# Game Manager
PLAYERS_PER_GAME = 2
GAMES = {
    "bomberman": {
        "gamefunc": Bomberman,
        "initfunc": (lambda: {"mapname": choice(listdir(pathjoin("game", "maps")))})
    }
}

# Log
LOG_FILE = "latest.log"
FILE_LEVEL = "DEBUG"
CONSOLE_LEVEL = "INFO"
KEEP_LOG = True

# Database
DB_TYPE = "sqlite"
DB_SQLITE_FILE = "storage.db"

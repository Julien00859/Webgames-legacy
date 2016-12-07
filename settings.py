from logging import DEBUG, INFO, WARNING, ERROR

# Python
PYTHON_REQUIRED_VERSION = (3, 5)

# Logging
LOG_CONSOLE = True
LOG_CONSOLE_LEVEL = INFO

LOG_FILE = True
LOG_FILE_LEVEL = INFO
LOG_FILE_DIR = "logs/"
LOG_FILE_NAME = "latest.log"
LOG_FILE_STORE = True

LOG_SQL = True
LOG_SQL_LEVEL = DEBUG

AUTH_HOST = "localhost"
AUTH_PORT = 14200
AUTH_HTTPS = True
if AUTH_HTTPS:
    AUTH_CERT_PATH = ""
    AUTH_KEY_PATH = ""

# Game
GAMES_DIR = "games/"
GAME_DEFAULT_FREQUENCY = 20


DB_URI = "sqlite:///data.db"
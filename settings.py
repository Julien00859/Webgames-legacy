from logging import DEBUG, INFO, WARNING, ERROR
from datetime import timedelta

# Python
REQUIRED_VERSION = (3, 5)

# Logging
LOG_CONSOLE = True
LOG_CONSOLE_LEVEL = DEBUG

LOG_FILE = True
LOG_FILE_LEVEL = INFO
LOG_FILE_DIR = "logs/"
LOG_FILE_NAME = "latest.log"
LOG_FILE_STORE = True

LOG_SQL = True
LOG_SQL_LEVEL = INFO

# Auth
AUTH_HOST = "0.0.0.0"
AUTH_PORT = 14200
AUTH_HTTPS = True
if AUTH_HTTPS:
    AUTH_CERT_PATH = "auth_server/cert.pem"
    AUTH_KEY_PATH = "auth_server/key.pem"

AUTH_PASSWORD_SALT = b"I'm not salty"

AUTH_TOKEN_EXPIRATION = timedelta(days=1)
AUTH_TOKEN_LENGTH = 32
AUTH_TOKEN_GENERATION_MAX_TRY = 100
AUTH_TOKEN_FREE_TIMEOUT = timedelta(seconds=10)

AUTH_WORKER_COUNT = 1

# Game
GAMES_DIR = "games/"
GAME_DEFAULT_FREQUENCY = 20


DB_URI = "postgresql+psycopg2://julien:@localhost:5432/webgames"

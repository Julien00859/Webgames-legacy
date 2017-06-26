from os import environ

API_URL = environ.get("API_URL", "https://api.webgames.")

SERVER_HOST = environ.get("SERVER_HOST", "0.0.0.0")
SERVER_TCP_PORT = int(environ.get("SERVER_TCP_PORT", 4170))
SERVER_WS_PORT = int(environ.get("SERVER_WS_PORT", 4171))
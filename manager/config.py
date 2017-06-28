from datetime import timedelta
from os import environ

from pytimeparse import parse as timeparse
from yaml import load as yaml_load

config_file = yaml_load(open("config.yml", "r"))
config_cast = {
    "SERVER_TCP_PORT": int,
    "SERVER_WS_PORT": int,
    "JWT_EXPIRATION_TIME": lambda value: timedelta(seconds=timeparse(value)),
    "PING_TIMEOUT": timeparse,
    "PING_HEART_BEAT": timeparse
}

for key, value in config_file.items():
    globals()[key] = config_cast.get(key, str)(value)

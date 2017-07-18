#!./venv/bin/python

from datetime import timedelta
from os import environ
import logging
from pytimeparse import parse as timeparse
from yaml import load as yaml_load

def parse_config():
    config_file = yaml_load(open("config.yml", "r"))
    config_cast = {
        "LOG_LEVEL": lambda value: getattr(logging, value),
        "SERVER_TCP_PORT": int,
        "SERVER_WS_PORT": int,
        "JWT_EXPIRATION_TIME": lambda value: timedelta(seconds=timeparse(value)),
        "PING_TIMEOUT": timeparse,
        "PING_HEARTBEAT": timeparse,
        "SSL": bool,
        "REDIS_PORT": int,
        "REDIS_DATABASE": int,
        "REDIS_PASSWORD": lambda value: None if value is None else value
    }

    for key, value in config_file.items():
        globals()[key] = config_cast.get(key, str)(environ.get(key, value))

if __name__ == "__main__":
    from pprint import pprint
    parse_config()
    pprint({key: value for key, value in globals().items() if key in config_file})

elif "config_parsed" not in globals():
    parse_config()
    globals()["config_parsed"] = True

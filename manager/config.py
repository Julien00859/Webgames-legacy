#!./venv/bin/python

"""Configuration handler, first check environ then config file"""

from datetime import timedelta
from os import environ
import logging
from pytimeparse import parse as timeparse
from yaml import load as yaml_load

__all__ = ["LOG_LEVEL", "API_URL",
           "MANAGER_HOST", "MANAGER_TCP_HOST", "MANAGER_WS_HOST",
           "JWT_EXPIRATION_TIME", "JWT_SECRET",
           "PING_HEARTBEAT", "PING_TIMEOUT",
           "USE_SSL", "SSL_CERT_FILE", "SSL_KEY_FILE",
           "REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD", "REDIS_DATABASE"]

def parse_config():
    """Parse the environ and the config file to set options in globals"""
    config_file = yaml_load(open("config.yml", "r"))
    config_cast = {
        "LOG_LEVEL": lambda value: getattr(logging, value),
        "MANAGER_TCP_PORT": int,
        "MANAGER_WS_PORT": int,
        "JWT_EXPIRATION_TIME": lambda value: timedelta(seconds=timeparse(value)),
        "PING_TIMEOUT": timeparse,
        "PING_HEARTBEAT": timeparse,
        "USE_SSL": bool,
        "REDIS_PORT": int,
        "REDIS_DATABASE": int,
        "REDIS_PASSWORD": lambda value: None if value is None else value
    }

    for key, value in config_file.items():
        globals()[key] = config_cast.get(key, str)(environ.get(key, value))

if __name__ == "__main__":
    from pprint import pprint
    parse_config()
    pprint({key: value for key, value in globals().items() if key in __all__})

elif "config_parsed" not in globals():
    parse_config()
    globals()["config_parsed"] = True

#!./venv/bin/python

from typing import get_type_hints
from functools import partial
from logging import getLogger
from asyncio import sleep as asyncsleep
import shared
from hashlib import sha1
from os import listdir
from os.path import join as pathjoin
from aioredis.errors import ReplyError

logger = getLogger(__name__)
redis_scripts_hashes = {
    file: sha1(open(pathjoin("redis_scripts", file), "r").read().encode()).digest() for file in listdir("redis_scripts")
}

def cast_using_type_hints(type_hints: dict, kwargs: dict):
    return {key: None if value is None else type_hints[key](value) for key, value in kwargs.items()}

def cast_list_using_type_hints(func, datas: list):
    castuth = partial(cast_using_type_hints, get_type_hints(func))
    return list(map(lambda d: func(**d), [castuth(d) for d in datas]))

async def call_later_coro(delay, coro, *args, **kwargs):
    logger.debug("Schedule async call for '%s' with args %s %s in %d secondes", coro.__name__, args, kwargs, delay)
    await asyncsleep(delay)
    logger.debug("Call '%s' with args %s %s", coro.__name__, args, kwargs)
    await coro(*args, **kwargs)

async def run_redis_script(script_name, keys, args):
    sha = redis_scripts_hashes[script_name]
    try:
        logger.debug("Run cached script %s with keys: %s, args: %s", script_name, keys, args)
        return await shared.redis.evalsha(sha, keys, args)
    except ReplyError as e:
        if not e.args[0].startswith("NOSCRIPT"):
            raise
        logger.debug("No cached script found. Upload full version")
        script = open(pathjoin("redis_scripts", script_name), "r").read()
        return await shared.redis.eval(script, keys, args)

def asyncpartial(func, *args, **keywords):
    async def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return await func(*args, *fargs, **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc

if __name__ == "__main__":
    from sys import argv
    from contextlib import suppress
    with suppress(IndexError):
        if argv[1] == "jwt":
            import jwt
            from config import *
            from uuid import uuid4

            print(jwt.encode({"type": argv[2], "id": str(uuid4())}, JWT_SECRET).decode())
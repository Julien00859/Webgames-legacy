#!./venv/bin/python

from asyncio import sleep as asyncsleep
from functools import partial
from hashlib import sha1
from logging import getLogger
from os import listdir
from os.path import join as pathjoin
from typing import get_type_hints
from aioredis.errors import ReplyError
import shared

logger = getLogger(__name__)
redis_scripts_hashes = {
    file: sha1(open(pathjoin("redis_scripts", file), "rb").read()).digest()
    for file in listdir("redis_scripts")
}

def cast_using_type_hints(type_hints: dict, kwargs: dict):
    """
    Given type_hints of function and some key word arguments,
    cast each kwarg with the type given by typehints
    except for None values, None in kwargs stay None
    """
    return {key: None if value is None else type_hints[key](value)
            for key, value in kwargs.items()}

async def call_later_coro(delay, coro, *args, **kwargs):
    """Asyncio.call_later but call a coroutine using await"""
    logger.debug("Schedule async call for '%s' with args %s %s in %d secondes",
                 coro.__name__, args, kwargs, delay)
    await asyncsleep(delay)
    logger.debug("Call '%s' with args %s %s", coro.__name__, args, kwargs)
    await coro(*args, **kwargs)

async def run_redis_script(script_name, keys, args):
    """Run redis script, try for a cached version, if fail upload the script"""
    sha = redis_scripts_hashes[script_name]
    try:
        logger.debug("Run cached script %s with keys: %s, args: %s", script_name, keys, args)
        return await shared.redis.evalsha(sha, keys, args)
    except ReplyError as err:
        if not err.args[0].startswith("NOSCRIPT"):
            raise
        logger.debug("No cached script found. Upload full version")
        script = open(pathjoin("redis_scripts", script_name), "r").read()
        return await shared.redis.eval(script, keys, args)

def asyncpartial(func, *args, **keywords):
    """functools.partial for async function"""
    async def newfunc(*fargs, **fkeywords):
        """wrapped async function"""
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return await func(*args, *fargs, **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc

if __name__ == "__main__":
    # Some useful tools
    from sys import argv
    from contextlib import suppress
    with suppress(IndexError):
        if argv[1] == "jwt":
            # Generate a JSON Web Token with a type given by argv[2]
            import jwt
            from config import JWT_SECRET
            from uuid import uuid4

            print(jwt.encode({"type": argv[2], "id": str(uuid4())}, JWT_SECRET).decode())

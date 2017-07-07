from collections import namedtuple, ChainMap
from datetime import datetime
from logging import getLogger
from random import randint
from time import time
from typing import get_type_hints, NamedTuple
import asyncio
import re

import jwt

from config import *
from tools import *
from server import redis
from games import start as game_start

logger = getLogger(__name__)
Ping = NamedTuple("Ping", [("value", int), ("time_sent", int)])
Command = namedtuple("Command", ["restricted_to", "pattern", "callback"])
command_re = re.compile("[\w-]+\.[\w-]+\.[\w-]+ [a-z0-9_]+( .*)?")

class DispatcherMeta(type):
    def __new__(mcs, name, bases, attrs):
        callbacks = ChainMap()
        maps = callbacks.maps
        for base in bases:
            if isinstance(base, DispatcherMeta):
                maps.extend(base.__callbacks__.maps)

        attrs["__callbacks__"] = callbacks
        attrs["dispatcher"] = property(lambda obj: callbacks)
        cls = super().__new__(mcs, name, bases, attrs)
        return cls

    def set_callbacks(cls, restricted_to, pattern, callback):
        cls.__callbacks__[callback.__name__] = Command(restricted_to, pattern, callback)
        return callback

    def register(cls, restricted_to, pattern):
        def wrapper(callback):
            return cls.set_callbacks(restricted_to, pattern, callback)
        return wrapper


class ClientHandler(metaclass=DispatcherMeta):
    clients = set()

    def __init__(self, peername, sendfunc, loop=None):
        """
        Initiate a new client with its socket and peername
        """
        self.__class__.add(self)

        self.peername = peername
        self.send = sendfunc

        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.closed = False

        self.jwt = None
        self.queue = None

        self.ping = None

        self.call_laters = {
            "ping": self.loop.create_task(self.send_ping())
        }

    def __str__(self):
        if self.jwt is None:
            return "undefined client at {}:{}".format(*self.peername)

        return "{} {}#{} at {}:{}".format(
            self.jwt["type"],
            self.jwt["name"],
            self.jwt["id"],
            *self.peername)

    async def dispatch(self, data: str):
        """
        Dispatch each command to the correct method
        """
        for line in filter(bool, data.splitlines()):
            match = command_re.match(line)
            if not match:
                logger.warning("Syntax error for line: %s", line)
                await self.send("error syntax error for line: " + line)
                continue

            jwt_payload, command, *args = line.split(" ", 2)
            args = args[0] if args else ""

            try:
                newjwt = jwt.decode(jwt_payload, JWT_SECRET)
                if self.jwt is None
                    self.jwt = newjwt
                elif self.jwt != newjwt:
                    await self.kick("New JWT is different from previous one")
                    return
            except Exception as e:
                await self.kick(e)
                return

            if command not in self.dispatcher:
                logger.warning("%s sent an unknown command: %s", str(self), command)
                await self.send("error command \"%s\" not found\r\n" % command)
                continue

            cmd = self.dispatcher[command]

            if cmd.restricted_to not in [None, self.jwt["type"]]:
                logger.warning("%s tried to use the command \"%s\"", str(self), command)
                await self.send("error command \"{}\" is not available for you\r\n".format(command))
                continue
            
            if cmd.pattern is not None:
                match = cmd.pattern.match(args)
                if not match:
                    logger.warning("%s has syntax error in command \"%s\" with args: %s", str(self), command, args)
                    await self.send("error syntax error in command \"{}\" with args: {}\r\n".format(command, args))
                    continue

                kwargs = cast_using_type_hints(
                    get_type_hints(cmd.callback), 
                    match.groupdict())
                logger.debug("Call %s with args %s", 
                    str(cmd.callback), 
                    str(kwargs))
                if asyncio.iscoroutinefunction(cmd.callback):
                    await cmd.callback(self, **kwargs)
                else:
                    cmd.callback(self, **kwargs)
            else:
                logger.debug("Call %s without args", str(cmd.callback))
                if asyncio.iscoroutinefunction(cmd.callback):
                    await cmd.callback(self)
                else:
                    cmd.callback(self)


    
    async def send_ping(self, value=None):
        """
        Send a ping request
        Schedule a kick for ping-timeout in the future
        """
        if self.ping is not None:
            raise RuntimeError("Ping pending")

        if value is None:
            value = randint(1000, 9999)
        self.ping = Ping(value, time())

        logger.debug("Send ping to %s", str(self))
        await self.send("ping {}\r\n".format(value))

        self.call_laters["ping-timeout"] = self.loop.create_task(
            call_later_coro(PING_TIMEOUT, self.kick, "ping timeout"))

    async def kick(self, reason: str=""):
        """
        Gentle close the connection with the client
        """
        logger.warning("Kick %s for %s", str(self), reason or "-no reason given-")
        if reason:
            await self.send("close {}\r\n".format(reason))
        else:
            await self.send("close\r\n")
        self.close()

    def close(self):
        for call in self.call_laters.values():
            call.cancel()
        self.closed = True
        self.__class__.clients.remove(self)
        

uuid = "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"

@ClientHandler.register(None, re.compile("(?P<reason>.*)?"))
def quit(client, reason: str=""):
    """
    Client is disconnecting, mark him as closed
    """
    logger.info("%s has closed the connection: %s", str(client), reason or "-no reason given-")
    client.close()

@ClientHandler.register(None, re.compile("(?P<value>[0-9]{4})"))
async def ping(client, value: int):
    """
    Recieve a ping, send back a pong with the same value
    """
    await client.send("pong {}\r\n".format(value))

@ClientHandler.register(None, re.compile("(?P<value>[0-9]{4})"))
async def pong(client, value: int):
    """
    Validate a pong answer from the client
    Schedule the next ping
    """
    if client.ping is None:
        await client.kick("no ping was sent")
    
    elif value != client.ping.value:
        await client.kick("wrong ping value")

    else:
        client.ping = None
        client.call_laters["ping-timeout"].cancel()
        client.call_laters["ping"] = client.loop.create_task(
            call_later_coro(PING_HEARTBEAT, client.send_ping))

@ClientHandler.register("api", re.compile("(?P<game>\S+)"))
async def enable(client, game: str):
    raise NotImplementedError()

@ClientHandler.register("api", re.compile("(?P<game>\S+)"))
async def disable(client, game: str):
    raise NotImplementedError()

@ClientHandler.register("api", re.compile("(?P<game>\S+)"))
async def remove(client, game: str):
    raise NotImplementedError()

@ClientHandler.register("user", re.compile("(?P<queue>\S+)"))
async def join(client, queue: str):
    if self.queue is not None:
        logging.warning("%s tried to join a queue but he is queued already")
        await client.send("error you are already in the queue: %s" % queue)
        return

    try:
        game = database.get_game(queue)
    except KeyError:
        logging.warning("%s tried to join an unkown queue: %s", str(client), queue)
        await client.send("error queue %s is unknown" % queue)
        return

    if not game.enabled:
        logging.warning("%s tried to join a disabled queue: %s", str(client), queue)
        await client.send("error queue %s is disabled" % queue)
        return

    players = await redis.eval("add_player_in_queue.lua", 
                               "3", 
                               queue, 
                               client.jwt["id"], 
                               game.threshold)
    self.queue = queue

    if players is not None:
        game_start(game, players)

@ClientHandler.register("user", None)
async def leave(client):
    if self.queue is None:
        logging.warning("%s tried to leave its queue but is not queued")
        await client.send("error not in queue")
        return

    try:
        game = database.get_game(queue)
    except KeyError:
        logging.warning("%s tried to leavee an unkown queue: %s", str(client), queue)
        await client.send("error queue %s is unknown" % queue)
        return

    cnt = await database.redis.lrem("queue:%s" % queue, client.jwt["id"])
    self.queue = None

@ClientHandler.register("game", re.compile("(?P<gameid>{})".format(uuid)))
async def gameover(client, gameid):
    pass
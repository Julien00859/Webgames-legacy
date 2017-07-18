from collections import namedtuple, ChainMap
from datetime import datetime
from logging import getLogger, WARNING
from random import randint
from time import time
from typing import get_type_hints, NamedTuple
import asyncio
import re

import jwt
from ujson import loads as ujsonloads

from config import PING_TIMEOUT, PING_HEARTBEAT, JWT_SECRET, API_URL
from tools import cast_using_type_hints, run_redis_script, call_later_coro
import shared
from games import run as run_game

logger = getLogger(__name__)
Ping = NamedTuple("Ping", [("value", int), ("time_sent", int)])
JWTData = namedtuple("JWTData", ["type", "id"])
GameData = namedtuple("GameData", ["name", "ports", "enabled", "threshold"])
Command = namedtuple("Command", ["restricted_to", "regexp", "callback"])
command_re = re.compile(r"[\w-]+\.[\w-]+\.[\w-]+ [a-z0-9_]+( .*)?")
spaces_re = re.compile(r"\s+")


class DispatcherMeta(type):
    """Dispatcher Pattern"""
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
        """Register a callback"""
        cls.__callbacks__[callback.__name__.strip("_")] = \
            Command(restricted_to, re.compile(pattern) if pattern else None, callback)
        return callback

    def register(cls, restricted_to, pattern):
        """Decorator for register a callback"""
        def wrapper(callback):
            return cls.set_callbacks(restricted_to, pattern, callback)
        return wrapper


class ClientHandler(metaclass=DispatcherMeta):
    """Handle a client, verify the JWT, dispatch the command"""
    def __init__(self, peername, sendfunc, loop=None):
        """
        Initiate a new client with its socket and peername
        """
        shared.clients.add(self)

        self.peername = peername
        self.send = sendfunc

        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.closed = False

        self.jwtdata = None

        self.ping = None

        self.call_laters = {
            "ping": self.loop.create_task(self.send_ping())
        }

    def __str__(self):
        if self.jwtdata is None:
            return "unknown client at {}:{}".format(*self.peername)

        return "{} {} at {}:{}".format(*self.jwtdata, *self.peername)

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
            logger.debug("Message from %s: <jwt> %s %s", str(self), command, args)

            try:
                newjwt = jwt.decode(jwt_payload, JWT_SECRET)
                if self.jwtdata is None:
                    self.jwtdata = JWTData(type=newjwt["type"], id=newjwt["id"])
                else:
                    assert self.jwtdata.id == newjwt["id"]
            except (jwt.InvalidTokenError, AssertionError) as err:
                await self.kick(err)
                return

            cmd = self.dispatcher.get(command)
            if cmd is None:
                logger.warning("%s sent an unknown command: %s", str(self), command)
                await self.send("error command \"%s\" not found\r\n" % command)
                continue

            if cmd.restricted_to not in [None, self.jwtdata.type]:
                logger.warning("%s tried to use the command \"%s\"", str(self), command)
                await self.send("error command \"{}\" is not available for you\r\n".format(command))
                continue

            if cmd.regexp is not None:
                match = cmd.regexp.match(args)
                if not match:
                    logger.warning("%s has syntax error in command \"%s\" with args: %s", str(self), command, args)
                    await self.send("error syntax error in command \"{}\" with args: {}\r\n".format(command, args))
                    continue

                kwargs = cast_using_type_hints(
                    type_hints=get_type_hints(cmd.callback),
                    kwargs=match.groupdict())
                logger.debug("Dispatch to '%s' with kwargs %s", cmd.callback.__name__, kwargs)

            else:
                kwargs = {}
                logger.debug("Dispatch to '%s' without kwargs", cmd.callback.__name__)

            try:
                if asyncio.iscoroutinefunction(cmd.callback):
                    await cmd.callback(self, self.jwtdata, **kwargs)
                else:
                    cmd.callback(self, self.jwtdata, **kwargs)
            except:
                logger.exception("Error in dispatched command")
                await self.send("error internal error please retry later...")

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

        await self.send("ping {}\r\n".format(value))

        self.call_laters["ping-timeout"] = self.loop.create_task(
            call_later_coro(PING_TIMEOUT, self.kick, "ping timeout"))

    async def kick(self, reason: str = "", level=WARNING):
        """
        Gentle close the connection with the client
        """
        logger.log(level, "Kick %s for %s", str(self), reason or "-no reason given-")
        if reason:
            await self.send("quit {}\r\n".format(reason))
        else:
            await self.send("quit\r\n")
        await self.close()

    async def close(self):
        """
        Free ressources used by the client and set the client as closed
        """
        self.closed = True
        logger.debug("Set %s as closed", str(self))
        for call in self.call_laters.values():
            call.cancel()
        if self.jwtdata is not None and self.jwtdata.type == "user":
            logger.debug("Remove user from cache")
            await run_redis_script("remove_player_from_queues.lua",
                                   [self.jwtdata.id],
                                   shared.queues)
        shared.clients.remove(self)


# ======== Shared commands ========

@ClientHandler.register(None, r"(?P<command>\S+)?")
async def help_(client, jwtdata, command: str = ""):
    """
    Show command list or help about a specific command.
    """
    cmds = []
    if command:
        cmd = client.__callbacks__.get(command)
        if cmd is None:
            await client.send('error command "{}" not found'.format(command))
            return
        await client.send("help {0}: {1} Usage: {0} {2}".format(\
                          command,
                          spaces_re.sub(" ", cmd.callback.__doc__).strip(),
                          cmd.regexp.pattern))
    else:
        await client.send("help command list: " + " ".join(client.__callbacks__.keys()))


@ClientHandler.register(None, r"(?P<reason>.*)?")
async def quit_(client, jwtdata, reason: str = ""):
    """
    Disconnect from the server.
    """
    logger.info("%s has closed the connection: %s", str(client), reason or "-no reason given-")
    await client.close()

@ClientHandler.register(None, r"(?P<value>[0-9]{4})")
async def ping(client, jwtdata, value: int):
    """
    Send a ping request with a four digit value.
    """
    await client.send("pong {}\r\n".format(value))

@ClientHandler.register(None, r"(?P<value>[0-9]{4})")
async def pong(client, jwtdata, value: int):
    """
    Response a ping request sent by the server.
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

# ======== API commands ========

@ClientHandler.register("api", r"(?P<game>\S+)")
async def enable(client, jwtdata, game: str):
    """
    Enable a game by allowing players to join its queue.
    """
    raise NotImplementedError()

@ClientHandler.register("api", r"(?P<game>\S+)")
async def disable(client, jwtdata, game: str):
    """
    Disable a game by kicking players from its queue and disallow players to join it.
    """
    raise NotImplementedError()

# ======== User commands ========

@ClientHandler.register("user", r"(?P<queue>\S+)")
async def join(client, jwtdata, queue: str):
    """
    Join a game by first joining its queue.
    """
    if (await shared.redis.exists("players:%s:game" % jwtdata.id)):
        logger.warning("%s tried to join a queue while beeing in game", str(client))
        await client.send("error cannot join a queue while in game")
        return

    if queue not in shared.queues:
        logger.warning("%s tried to join the queue %s", str(client), queue)
        await client.send("error this game is not available")
        return

    async with shared.http.get(API_URL + "/queues/" + queue) as resp:
        if resp.status != 200:
            logger.error("Status code for '%s' is not 200: %d",
                         API_URL + "/queues" + queue, resp.status)
            await client.send("error internal error")
            return

        game = GameData(name=queue, **(await resp.json(loads=ujsonloads)))

    players_ids = await run_redis_script("add_player_in_queue.lua",
                                         [queue, jwtdata.id, game.threshold],
                                         shared.queues)

    logger.info("%s joined queue %s", str(client), queue)

    if players_ids is not None:
        players_ids = list(map(lambda b: b.decode(), players_ids))
        logger.info("Game '%s' filled with %d players", queue, game.threshold)
        client.loop.create_task(run_game(game, players_ids))

@ClientHandler.register("user", None)
async def leave(client, jwtdata):
    """
    Leave a queue.
    """
    raise NotImplementedError()

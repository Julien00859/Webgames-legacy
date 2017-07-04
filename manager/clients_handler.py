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

logger = getLogger(__name__)
Ping = NamedTuple("Ping", [("value": int), ("time_sent": int)])
Command = NamedTuple("Command", [("restricted_to": str), ("pattern": re.compile)])
command_re = re.compile("[\w-]+\.[\w-]+\.[\w-]+ [a-z0-9_]+( .*)?")
uuid = "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
commands = {
    "quit":     Command(None, re.compile("(?P<reason>.*)?")),
    "ping":     Command(None, re.compile("(?P<value>[0-9]{4})")),
    "pong":     Command(None, re.compile("(?P<value>[0-9]{4})")),

    "add":      Command("api", re.compile("(?P<game>\S+)")),
    "remove":   Command("api", re.compile("(?P<game>\S+)")),
    "enable":   Command("api", re.compile("(?P<game>\S+)")),
    "disable":  Command("api", re.compile("(?P<game>\S+)")),

    "join":     Command("user", re.compile("(?P<queue>\S+)")),
    "leave":    Command("user", re.compile("(?P<queue>\S+)")),

    "gameover": Command("game", re.compile("(?<gameid>{})".format(uuid)))
}
jwt_claims = lambda: {
    "iss": "manager",
    "sub": "webgames",
    "iat": datetime.utcnow(), 
    "exp": datetime.utcnow() + JWT_EXPIRATION_TIME
}

class ClientHandler:
    def __init__(self, peername, sendfunc, closefunc, loop=None):
        """Initiate a new client with its socket and peername"""
        self.peername = peername
        self.send = sendfunc
        self.close = closefunc

        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.closed = False

        self.jwt = None

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

    async def evaluate(self, data: str):
        for line in data.splitlines():
            match = command_re.match(line)
            if not match:
                logger.warning("Syntax error for line: %s", line)
                await self.send("error syntax error for line: " + line)
                continue

            jwt_payload, command, args = line.split(" ", 2)
            args = args if args else ""

            try:
                self.jwt = jwt.decode(jwt_payload, JWT_SECRET)
            except Exception as e:
                await self.kick(e)
                return

            if command not in commands:
                logger.warning("%s sent an unknown command: %s", str(self), line)
                await self.send("error command \"{}\" not found\r\n".format(line))
                continue

            if commands[command].restricted_to not in [None, self.jwt["type"]]:
                logger.warning("%s tried to use the command \"%s\"", str(self), command)
                await self.send("error command \"{}\" is not available for you\r\n".format(command))
                continue
            
            match = commands[command].pattern.match(args)
            if not match:
                logger.warning("%s has syntax error in command \"%s\" with args: %s", str(self), command, args)
                await self.send("error syntax error in command \"{}\" with args: {}\r\n".format(command, args))
                continue

            func = getattr(self, command)
            kwargs = cast_using_type_hints(get_type_hints(func), match.groupdict())
            logger.debug("Call %s with args %s", str(func), str(kwargs))
            if asyncio.iscoroutinefunction(func):
                await func(**kwargs)
            else:
                func(**kwargs)

    
    async def send_ping(self, value=None):
        """Send a ping request to the client"""
        if self.ping is not None:
            raise RuntimeError("Ping pending")

        if value is None:
            value = randint(1000, 9999)
        self.ping = Ping(value, time())

        logger.debug("Send ping to %s", str(self))
        await self.send("ping {}\r\n".format(value))

        self.call_laters["kick"] = self.loop.create_task(call_later_coro(PING_TIMEOUT, self.kick, "ping timeout"))

    async def kick(self, reason: str=""):
        logger.warning("%s is kicked because of: %s", str(self), reason or "-no reason given-")
        if reason:
            await self.send("close {}\r\n".format(reason))
        else:
            await self.send("close\r\n")

        for call in self.call_laters.values():
            call.cancel()
        self.closed = True

        if asyncio.iscoroutinefunction(self.close):
            await self.close()
        else:
            self.close()

    def quit(self, reason: str=""):
        """Recieve a close request, mark the client as closed"""
        logger.info("%s has closed the connection: %s", str(self), reason or "-no reason given-")
        for call in self.call_laters.values():
            call.cancel()
        self.closed = True

    async def ping(self, value: int):
        """Recieve a ping request from the client, send back a pong"""
        await self.send("pong {}\r\n".format(value))

    async def pong(self, value: int):
        """Recieve a pong answer from the client, validate the pong and update statistics"""
        if self.ping is None:
            await self.kick("no ping was sent")
        
        elif value != self.ping.value:
            await self.kick("wrong ping value")

        else:
            self.ping = None
            self.call_laters["kick"].cancel()
            self.call_laters["ping"] = self.loop.create_task(call_later_coro(PING_HEARTBEAT, self.send_ping))
    
    async def enable(self, game: str):
        pass

    async def disable(self, game: str):
        pass

    async def add(self, game: str):
        pass

    async def remove(self, game: str):
        pass

    async def join(self, queue: str):
        # redis

    async def leave(self, queue: str):
        pass

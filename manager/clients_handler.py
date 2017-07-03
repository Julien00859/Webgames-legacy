from collections import namedtuple, deque
from datetime import datetime
from logging import getLogger
from random import randint
from time import time
from typing import get_type_hints
import asyncio
import re
from itertools import count

import jwt

from config import *

counter = count()

async def call_later_coro(timeout, coro, *args, **kwargs):
    call_id = next(counter)
    logger.debug("Schedule async call for %s with args %s %s in %d secondes (Call ID #%d)", coro, args, kwargs, timeout, call_id)
    await asyncio.sleep(timeout)
    logger.debug("Await call ID #%d", call_id)
    await coro(*args, **kwargs)
    logger.debug("Call ID #%d awaited", call_id)

logger = getLogger(__name__)
Ping = namedtuple("Ping", ["value", "time_sent"])
Command = namedtuple("Command", ["restricted_to", "pattern"])
command_re = re.compile("[\w-]+\.[\w-]+\.[\w-]+ \w+( .*)?")
commands = {
    "quit":     Command(None, re.compile("(?P<reason>.*)?")),
    "ping":     Command(None, re.compile("(?P<value>[0-9]+)")),
    "pong":     Command(None, re.compile("(?P<value>[0-9]+)")),

    "add":      Command("api", re.compile("(?P<game>\S+)")),
    "remove":   Command("api", re.compile("(?P<game>\S+)")),
    "enable":   Command("api", re.compile("(?P<game>\S+)")),
    "disable":  Command("api", re.compile("(?P<game>\S+)")),

    "join":     Command("user", re.compile("(?P<queue>\S+)")),
    "leave":    Command("user", re.compile("(?P<queue>\S+)"))
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
        self.delais = deque(maxlen=10)

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
            kwargs = {key: get_type_hints(func)[key](value) if value is not None else "" for key, value in match.groupdict().items()}
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
            self.delais.append(time() - self.ping.time_sent)
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
        pass

    async def leave(self, queue: str):
        pass

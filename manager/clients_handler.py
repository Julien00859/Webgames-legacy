from collections import namedtuple, deque
from logging import getLogger
import asyncio
from random import randint
from time import time
import re
from typing import get_type_hints
import jwt

logger = getLogger(__name__)
Ping = namedtuple("Ping", ["value", "time_sent"])
Command = namedtuple("Command", ["restricted_to", "pattern"])

class ClientHandler:
    command_re = re.compile("[\w-]+\.[\w-]+\.[\w-]+ \w+( .*)?")
    commands = {
        "quit":     Command(None, re.compile("(?P<reason>.*))?")),
        "ping":     Command(None, re.compile("(?P<value>[0-9]+)")),
        "pong":     Command(None, re.compile("(?P<value>[0-9]+)")),

        "add":      Command("api", re.compile("(<?P<game>\S+)")),
        "remove":   Command("api", re.compile("(<?P<game>\S+)"))
        "enable":   Command("api", re.compile("(?P<game>\S+)")),
        "disable":  Command("api", re.compile("(?P<game>\S+"))
    }
    
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
            "ping" = self.loop.call_soon(self.send_ping)
        }

    def __str__(self):
        return "{type} {name}#{id} at {host}:{port}".format(
            self.jwt["clienttype"].title(),
            self.jwt["username"],
            self.jwt["_id"],
            *self.peername)

    async def evaluate(self, data: str):
        for line in data.splitlines():
            match = command_re.match(line)
            if not match:
                logger.warning("Syntax error for line: %s", line)
                await self.send("error syntax error for line: %s", line)
                continue

            jwt_payload, command, args = line.split(" ", 2)
            args = args if args else ""

            try:
                self.jwt = jwt.decode(jwt_payload)
            except Exception as e:
                logger.warning("[%s] %s", str(self), e.message)
                self.kick(e.message)

            if command not in commands
                logger.warning("[%s] Command \"%s\" not found", line)
                await self.send("error command \"{}\" not found\r\n".format(line))
                continue

            if commands[command].restricted_to not in [None, jwt.clienttype]:
                logger.warning("[%s] Command \"%s\" not available to %s", str(self), command, jwt.clienttype)
                await self.send("error command \"{}\" is not available for you\r\n".format(command.name))
                continue
            
            match = commands[command].pattern.match(args)
            if not match:
                logger.warning("[%s] Syntax error for command \"%s\" with args: %s", str(self), command, args)
                await self.send("error syntax error for command \"{}\" with args: {}\r\n".format(command, args))
                continue

            func = getattr(self, command)
            await func(jwt, **{key: get_type_hints(func)[key](value) if value is not None else "" for key, value in match.groupdict().items()})
    
    async def send_ping(self, value=None):
        """Send a ping request to the client"""
        if self.ping is not None:
            raise RuntimeError("Ping was already sent")

        if value is None:
            value = randint(1000, 9999)
        self.ping = Ping(value, time())
        await self.send("ping {}\r\n".format(value))

        self.call_laters["kick"] = self.loop.call_later(30, self.kick, "ping timeout")

    async def kick(self, reason: str=""):
        logger.warning("Client %s is kicked because of: %s", str(self), reason or "-no reason given-")
        if reason:
            await self.send("close {}\r\n".format(reason))
        else:
            await self.send("close\r\n")

        for call in self.call_laters.value():
            call.cancel()
        self.closed = True

        if asyncio.iscoroutinefunction(self.close):
            await self.close()
        else:
            self.close()

    def quit(self, reason: str=""):
        """Recieve a close request, mark the client as closed"""
        logger.info("Client %s has closed the connexion: %s", str(self), reason or "-no reason given-")
        for call in self.call_laters.value():
            call.cancel()
        self.closed = True

    async def ping(self, value: int):
        """Recieve a ping request from the client, send back a pong"""
        self.send("pong {}\r\n".format(value))

    async def pong(self, value: int):
        """Recieve a pong answer from the client, validate the pong and update statistics"""
        if self.ping is None:
            await self.kick("no ping was sent")
        
        elif value != self.ping.value:
            await self.kick("wrong ping value")

        else:
            self.delais.append(time() - self.ping.time)
            self.ping = None
            self.call_laters["ping"] = self.loop.call_later(30, self.send_ping)
    
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

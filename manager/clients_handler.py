from collections import namedtuple, deque
from logging import getLogger
import asyncio
from websockets.server import WebSocketServerProtocol
from random import randint
from time import time
import re

logger = getLogger(__name__)
Ping = namedtuple("Ping", ["value", "time_sent"])
Command = namedtuple("Command", ["name", "restricted_to", "pattern", "types"])

def enum(name, values):
    return namedtuple(name, list(map(str, values)))(*range(len(values)))
ClientType = enum("ClientType", ["none", "user", "api", "game"])

class ClientHandler:
    commands = [
        Command("close", ClientType.none, re.compile("close( (?P<reason>.*))?"), {"reason": str},
        Command("ping", ClientType.none, re.compile("ping (?P<value>[0-9]+)"), {"value": int}),
        Command("pong", ClientType.none, re.compile("pong (?P<value>[0-9]+)"), {"value": int}),

        Command("auth", ClientType.user, re.compile("auth (?P<jwt>[\w-]+\.[\w-]+\.[\w-]+)"), {"jwt": str}),

        Command("enable", ClientType.api, re.compile("enable (?P<game>\S+)"), {"game": str}),
        Command("disabled", ClientType.api, re.compile("disable (?P<game>\S+"), {"game": str})
    ]

    def __init__(self, socket, peername, clienttype, loop=None):
        """Initiate a new client with its socket and peername"""
        self.socket = socket
        self.peername = peername
        self.clienttype = clienttype
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.close = False

        self.ping = None
        self.ping_timeout = None
        self.ping_delayed = None
        self.pings = deque(maxlen=10)

        if isinstance(socket, asyncio.StreamWriter):
            self.send = self.send_tcp
        elif isinstance(socket, WebSocketServerProtocol):
            self.send = self.send_ws
        else:
            raise TypeError("socket type {} not supported".format(type(socket)))

        await self.send_ping()

    def __str__(self):
        """Return the peername as "address:port""""
        return "{}:{}".format(*self.peername)

    def __repr__(self):
        return "<{} at {!s}>".format(self.__class__.__name__, self)
    
    async def send_ws(msg):
        """Send method to use when the socket is a websocket"""
        await self.socket.send(msg + "\r\n")

    async def send_tcp(msg):
        """Send method to use when the socket is a tcp socket"""
        self.socket.write((msg + "\r\n").encode())
        await self.socket.drain()

    async def evaluate(data):
        for line in data.split("\r\n"):
            for command in self.__class__.commands:
                match = command.pattern.match(line)
                if match:
                    if command.restricted_to == ClientType.none or command.restricted_to == self.clienttype:
                        await getattr(self, command.name)(**{key: command.types[key](value) for key, value})
                        if self.close:
                            return
                    else:
                        logger.warning("Command \"%s\" not available to %d", command.name, self.clienttype)
                        await self.send("error command \"{}\" is not available for you".format(command.name))
            else:
                logger.warning("Command \"%s\" from %s didn't match any", line, repr(self))
                await self.send("error command \"{}\" didn't match any command available".format(line))
    
    async def send_ping(self, value=None):
        """Send a ping request to the client"""
        if value is None:
            value = randint(1000, 9999)
        self.ping = Ping(value, time())
        await self.send("ping {}".format(value))
    
    # Callback for received commands
    async def ping(self, value):
        """Recieve a ping request from the client, send back a pong"""
        self.send("pong {}".format(value))

    async def pong(self, value):
        """Recieve a pong answer from the client, validate the pong and update statistics"""
        if self.ping is None:
            await self.send("close no ping was sent")
            self.close()
        
        elif value != self.ping.value:
            await self.send("close wrong ping value")
            self.close()

        else:
            self.pings.append(time() - self.ping.time)
            self.ping = None

            self.ping_delayed = asyncio.Task(self.send_ping)
            self.loop.call_later(30, self.ping_delayed)

    async def close(self, reason=None):
        """Recieve a close request, mark the client as closed"""
        self.close = True
        if isinstance(self.ping_delayed, asyncio.Task) and not self.ping_delayed.canceled:
            self.ping_delayed.cancel()

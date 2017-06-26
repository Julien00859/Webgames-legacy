from collections import namedtuple, deque
from logging import getLogger
from asyncio import StreamWriter
from websockets.server import WebSocketServerProtocol
from random import randint
from time import time
import re

logger = getLogger(__name__)

Ping = namedtuple("Ping", ["value", "time_sent"])
Command = namedtuple("Command", ["name", "restricted_to", "pattern", "args"])

def enum(name, values):
    return namedtuple(name, list(map(str, values)))(*range(len(values)))

ClientType = enum("ClientType", [None, "User", "API", "Game"])

class ClientHandler:
    commands = [
        Command("close", ClientType.None, re.compile("close(\s(.*))?"), [2]),
        Command("ping", ClientType.None, re.compile("ping ([0-9]+)"), [1]),
        Command("pong", ClientType.None, re.compile("pong ([0-9]+)"), [1]),
        Command("auth", ClientType.None, re.compile("auth (jwt)"), [1])
    ]

    def __init__(self, socket, peername):
        """Initiate a new client with its socket and peername"""
        self.socket = socket
        self.peername = peername
        self.close = False

        self.ping = None
        self.pings = deque(maxlen=10)

		if isinstance(socket, StreamWriter):
			self.send = lambda cmd: self.send_tcp(cmd + "\r\n")
		elif isinstance(socket, WebSocketServerProtocol):
			self.send = lambda cmd: self.send_ws(cmd + "\r\n")
		else:
			raise TypeError("socket type {} not supported".format(type(socket)))

    def __str__(self):
        """Return the peername as "address:port""""
        return "{}:{}".format(*self.peername)

    def __repr__(self):
        return "<{} at {!s}>".format(self.__class__.__name__, self)
    
	async def send_ws(msg):
        """Send method to use when the socket is a websocket"""
		await self.socket.send(msg)

	async def send_tcp(msg):
        """Send method to use when the socket is a tcp socket"""
		self.socket.write(msg.encode())
		await self.socket.drain()

    async def evaluate(data):
		for line in data.split("\r\n"):
            for command in self.__class__.commands:
                match = command.pattern.match(line)
                if match:
				    await getattr(self, command.name)(*map(lambda i: match.group(i), command.args))
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
    async def ping(self, value, *_):
        """Recieve a ping request from the client, send back a pong"""
        self.send("pong {}".format(value))

    async def pong(self, value, *_):
        """Recieve a pong answer from the client, validate the pong and update statistics"""
        if self.ping is None:
            await self.send("close no ping was sent")
            self.close = True
        
        elif value != self.ping.value:
            await self.send("close wrong ping value")
            self.close = True

        else:
            self.pings.append(time() - self.ping.time)
            self.ping = None

    async def close(self, *reason):
        """Recieve a close request, mark the client as closed"""
        self.close = True

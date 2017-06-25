from collections import namedtuple
from logging import getLogger
from asyncio import StreamWriter
from websockets.server import WebSocketServerProtocol

logger = getLogger(__name__)

class Server:
	commands = [
		"ping",
		"pong",
		"close"
	]

	def __init__(self, socket, peername):
		self.socket = socket
		self.peername = peername
		self.close = False

		if isinstance(socket, StreamWriter):
			self.send = self.send_tcp
		elif isinstance(socket, WebSocketServerProtocol):
			self.send = self.send_ws
		else:
			raise TypeError("socket type {} not supported".format(type(socket)))

	def __str__(self):
		return "{}:{}".format(*self.peername)

	def __repr__(self):
		return "<Server at {}:{}>".format(*self.peername)

	async def send_ws(msg):
		await self.socket.send(msg)

	async def send_tcp(msg):
		self.socket.write(msg.encode())
		await self.socket.drain()

	async def eval(self, message):
		for line in message.split("\r\n"):
			args = message.split(" ")
			if args[0] in Server.commands:
				await getattr(self, args[0])(args[1:])
			else:
				logger.warning('Command "%s" not found', args[0])
				await self.send('error command "{}" not found'.format(args[0]))

	async def ping(value, *_):
		await self.send("pong {}".format(value))

	async def pong(value, *_):
		pass

	async def close(*_):
		self.close = True
		

class User(Server):
	Command = namedtuple("Command", ["name", "auth_required"])
	commands = [
		Command("ping", False),
		Command("pong", False),
		Command("close", False),
		Command("auth", False),
		Command("join", True),
		Command("leave", True)
	]

	def __init__(self, socket, peername):
		super().__init__(self, socket, peername)
		self.is_authed = False		

	def __repr__(self):
		return "<User at {}>".format(self.peername)


	async def eval(self, message):
		for line in  message.split("\r\n"):
			args = line.split(" ")
			for cmd in User.commands:
				if args[0] == cmd.name:
					if self.is_authed or not cmd.auth_required:
						await getattr(self, args[0])(args[1:])
					else:
						logger.warning('Command "%s" was sent before successful "auth" one', args[0])
						await self.send('error command "{}" can only be used after authentication'.format(args[0]))
			else:
				logger.warning('Commands "%s" not found', args[0])
				await self.send('error command "{}" not found'.format(args[0]))
		

	async def auth(jwt, *_):
		if jwt:
			self.is_authed = True
			await self.send("success")
		else:
			logger.warning("Peer %s failed to authenticate", self)
			await self.send("error")

	async def join(queue, *_):
		pass

	async def leave(*_):
		pass


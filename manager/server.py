#!./venv/bin/python

import aiohttp
import asyncio
import uvloop
import logging
import websockets
import signal
from os import environ

from clients_handler import ClientHandler, ClientType
from config import *

logger = logging.getLogger(__name__)


async def tcp_handler(reader, writer):

	async def send(message: str):
		writer.send(message.encode())
		await writer.drain()

	client = ClientHandler(writer.get_extra_info("peername"), ClientType.user, send)

	logger.info("New TCP connection from %s", client)
	while True:
		try:
			data = await reader.read(65536).decode()
		except ConnectionResetError as e:
			logger.warning("Connection reset by peer %s:%d", client)
			break
		except:
			logger.exception("Exception while reading data from %s:%d.", client)
			break

		logger.debug("Message from %s:%d: %s", client, msg)
		if msg == "":
			logger.warning("Empty payload from %s:%d. Assume connection closed by peer", client)
			break

		client.evaluate(msg)
		if client.close:
			break
		
	writer.close()
	logger.info("Connection with %s closed", client)


async def ws_handler(ws, path):
	async def send(message: str):
		await ws.send(message)

	client = ClientHandler(ws.remote_address, ClientType.user, send)

	logger.info("New WS connection from %s", client)
	while True:
		try:
			data = await ws.recv()
			if not data:
				logger.warning("Empty payload from %s. Assume connection closed by peer", client)
				break
			if data is bytes:
				data = data.decode()
		except websockets.exceptions.ConnectionClosed:
			logger.warning("Connection closed by peer %s", client)
			break
		except:
			logger.exception("Exception while reading data from %s.", client)
			break

		client.evaluate(data)
		if client.close:
			break

	await ws.close()
	logger.info("Connection with %s closed", client)
			

def main():
	# Setup logging
	logging.root.level = logging.NOTSET
	stdout = logging.StreamHandler()
	stdout.level = getattr(logging, environ.get("LOG_LEVEL", "DEBUG"))
	stdout.formatter =  logging.Formatter(
		"{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{")
	logging.root.addHandler(stdout)
	
	# Setup asyncio
	asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
	loop = asyncio.get_event_loop()

	# Setup servers
	logger.info("Init Raw TCP Server on %s:%d", SERVER_HOST, SERVER_TCP_PORT)
	tcp_coro = asyncio.start_server(tcp_handler, SERVER_HOST, SERVER_TCP_PORT, loop=loop)
	tcp_server = loop.run_until_complete(tcp_coro)

	logger.info("Init Raw WebSocket Server on %s:%d", SERVER_HOST, SERVER_WS_PORT)
	ws_coro = websockets.serve(ws_handler, SERVER_HOST, SERVER_WS_PORT, loop=loop)
	ws_server = loop.run_until_complete(ws_coro)

	# Handle SIGTERM
	stop = asyncio.Future()
	loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

	# Start listening
	logger.info("Listening...")
	try:
		loop.run_until_complete(stop)
	except KeyboardInterrupt:
		logger.info("KeyboardInterrupt received")
	except:
		logger.exception("Fatal error")
	else:
		logger.info("SIGTERM received")

	logger.info("Shutting down servers")
	tcp_server.close()
	ws_server.close()
	loop.run_until_complete(tcp_server.wait_closed())
	loop.run_until_complete(ws_server.wait_closed())
	loop.close()

if __name__ == "__main__":
	main()

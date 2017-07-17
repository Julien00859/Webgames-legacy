#!./venv/bin/python

from os import environ
import asyncio
import logging
import signal
import ssl
from uuid import uuid4

from aiohttp import ClientSession
from aioredis import create_redis
import aiohttp
import ujson
import uvloop
import websockets

import shared
from clients_handler import ClientHandler
from config import *

logger = logging.getLogger(__name__)

async def tcp_handler(reader, writer):
    async def send(message: str):
        writer.write(message.encode())
        await writer.drain()

    client = ClientHandler(writer.get_extra_info("peername"), send)

    logger.info("New TCP connection from %s:%d", *client.peername)
    while True:
        try:
            data = await reader.read(4096)
        except ConnectionResetError as e:
            if not client.closed:
                logger.warning("Connection reset by %s", str(client))
            break
        
        if reader.at_eof():
            logger.debug("EOF reveived from %s", str(client))
            break
        
        try:
            msg = data.decode()
        except:
            if not client.closed:
                logger.exception("Exception while reading data from %s.", str(client))
            break

        logger.debug("Message from %s: %s", str(client), msg)
        if msg == "":
            logger.warning("Empty payload from %s. Assume connection closed by peer", str(client))
            break

        await client.dispatch(msg)
        if client.closed:
            break
    
    if not client.closed:
        await client.close()
    writer.close()
    logger.info("Connection with %s closed", str(client))


async def ws_handler(ws, path):
    async def send(message: str):
        await ws.send(message)

    client = ClientHandler(ws.remote_address, send)

    logger.info("New WS connection from %s", str(client))
    while True:
        try:
            data = await ws.recv()
            if not data:
                logger.warning("Empty payload from %s. Assume connection closed by peer", str(client))
                break
            if data is bytes:
                data = data.decode()
        except websockets.exceptions.ConnectionClosed:
            if not client.closed:
                logger.warning("Connection closed by peer %s", str(client))
            break
        except:
            logger.exception("Exception while reading data from %s.", str(client))
            break

        await client.dispatch(data)
        if client.closed:
            break
    
    if not client.closed:
        await client.close()
    await ws.close()
    logger.info("Connection with %s closed", str(client))


def main():
    shared.manager_id = uuid4()

    # Setup logging
    logging.root.level = logging.NOTSET
    stdout = logging.StreamHandler()
    stdout.level = LOG_LEVEL
    stdout.formatter =  logging.Formatter(
        "{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{")
    logging.root.addHandler(stdout)

    logger.info("Manager ID is %s", shared.manager_id)
    
    # Setup asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # Setup SSL
    if SSL:
        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sc.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)

    # Setup servers
    # TCP
    logger.info("Init %s TCP Server on %s:%d", 
                "Secure" if SSL else "Insecure",
                SERVER_HOST, 
                SERVER_TCP_PORT)
    tcp_coro = asyncio.start_server(tcp_handler,
                                    SERVER_HOST, 
                                    SERVER_TCP_PORT, 
                                    ssl=sc if SSL else None, 
                                    loop=loop)
    tcp_server = loop.run_until_complete(tcp_coro)

    # WebSocket
    logger.info("Init %s WebSocket Server on %s:%d", 
                "Secure" if SSL else "Insecure",
                SERVER_HOST, 
                SERVER_WS_PORT)
    ws_coro = websockets.serve(ws_handler,
                               SERVER_HOST,
                               SERVER_WS_PORT,
                               ssl=sc if SSL else None,
                               loop=loop)
    ws_server = loop.run_until_complete(ws_coro)

    # Setup clients
    # Redis
    logger.info("Connect to %s Redis Server at %s:%d on database %d %s password",
                "Secure" if SSL else "Insecure",
                REDIS_HOST, 
                REDIS_PORT,
                REDIS_DATABASE,
                "without" if REDIS_PASSWORD is None else "with")
    redis_coro = create_redis((REDIS_HOST, REDIS_PORT),
                               db=REDIS_DATABASE,
                               password=REDIS_PASSWORD,
                               ssl=sc if SSL else None,
                               loop=loop)
    shared.redis = loop.run_until_complete(redis_coro)

    # HTTP
    logger.info("Setup HTTP Client session")
    shared.http = ClientSession(json_serialize=ujson.dumps, loop=loop)
    async def get_queues():
        async with shared.http.get(API_URL + "/queues") as resp:
            assert resp.status == 200
            shared.queues = set(await resp.json(loads=ujson.loads))
    loop.run_until_complete(get_queues())
    

    # Handle SIGTERM for clean exit
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

    async def kick_all_clients():
        kicking = [client.kick("Server is shutting down...", level=logging.DEBUG) for client in shared.clients.copy()]
        await asyncio.wait(kicking)
    if len(shared.clients) > 0:
        logger.info("Kicking clients...")
        loop.run_until_complete(kick_all_clients())

    logger.info("Shutting down servers")
    tcp_server.close()
    ws_server.close()
    shared.redis.close()
    shared.http.close()
    loop.run_until_complete(tcp_server.wait_closed())
    loop.run_until_complete(ws_server.wait_closed())
    loop.run_until_complete(shared.redis.wait_closed())
    loop.close()

if __name__ == "__main__":
    main()

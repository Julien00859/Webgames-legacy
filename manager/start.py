#!./venv/bin/python

import asyncio
import logging
import pickle
import signal
import ssl
from datetime import datetime
from uuid import uuid4

from aiohttp import ClientSession
from aioredis import create_redis
import jwt
import ujson
import uvloop
import websockets

import shared
from tools import DispatcherMeta, get_connected_users
from clients_handler import ClientHandler
from games import run as rungame
from config import LOG_LEVEL, API_URL, JWT_SECRET, \
                   MANAGER_HOST, MANAGER_TCP_PORT, MANAGER_WS_PORT, UDP_BROADCASTER_PORT, \
                   USE_SSL, SSL_CERT_FILE, SSL_KEY_FILE, \
                   REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB_MANAGER

logger = logging.getLogger(__name__)

async def tcp_handler(reader, writer):
    """Handle a TCP Client"""

    async def send(message: str):
        """Send function used in ClientHandler"""
        logger.debug("Send %s to %s", message.splitlines(), str(client))
        writer.write(message.encode())
        await writer.drain()

    client = ClientHandler(writer.get_extra_info("peername"), send)

    logger.info("New TCP connection from %s:%d", *client.peername)
    while True:
        try:
            data = await reader.read(4096)
        except ConnectionResetError:
            if not client.closed:
                logger.warning("Connection reset by %s", str(client))
            break

        if reader.at_eof():
            logger.debug("EOF reveived from %s", str(client))
            break

        try:
            msg = data.decode()
        except UnicodeDecodeError:
            if not client.closed:
                logger.exception("Exception while reading data from %s.", str(client))
            break

        if msg == "":
            logger.warning(
                "Empty payload from %s. Assume connection closed by peer", str(client))
            break

        await client.dispatch(msg)
        if client.closed:
            break

    if not client.closed:
        await client.close()
    writer.close()
    logger.info("Connection with %s closed", str(client))


async def ws_handler(ws, path):
    """Handler a WebSocket client"""

    async def send(message: str):
        """Send function used by ClientHandler"""
        logger.debug("Send %s to %s", message.splitlines(), str(client))
        await ws.send(message)

    client = ClientHandler(ws.remote_address, send)

    logger.info("New WS connection from %s", str(client))
    while True:
        try:
            data = await ws.recv()
            if not data:
                logger.warning(
                    "Empty payload from %s. Assume connection closed by peer", str(client))
                break
            if data is bytes:
                data = data.decode()
        except websockets.exceptions.ConnectionClosed:
            if not client.closed:
                logger.warning("Connection closed by peer %s", str(client))
            break
        except UnicodeDecodeError:
            logger.warning("Can't decode data from %s.", str(client))
            break

        await client.dispatch(data)
        if client.closed:
            break

    if not client.closed:
        await client.close()
    await ws.close()
    logger.info("Connection with %s closed", str(client))

class UDPBroadcaster(metaclass=DispatcherMeta):
    def connection_made(self, transport):
        """on connection made"""
        port = transport.get_extra_info("sockname")[1]
        action = "listening" if port == UDP_BROADCASTER_PORT else "connected"
        logger.debug("%s %s on port %i", self.__class__.__name__, action, port)

    def datagram_received(self, data, addr):
        """on datagram reveived"""
        did, *objs = pickle.loads(data)
        logger.debug("Datagram id '%s' from %s:%d", did, *addr)
        func = self.__callbacks__.get(did)
        if not func:
            logger.error("%s is not registered as callback", did)
            return
        elif asyncio.iscoroutinefunction(func):
            asyncio.ensure_future(func(addr, *objs))
        else:
            func(addr, *objs)

    def connection_lost(self, exc):
        """on connection lost"""
        if exc:
            logger.error("Err", exc_info=exc)

@UDPBroadcaster.register()
async def relay_to_players(sender, players_ids, payload):
    """Relay message to our players"""
    for client in get_connected_users(players_ids):
        await client.send(payload)

@UDPBroadcaster.register()
async def readycheck(sender, players_ids, game_name, game_id):
    shared.ready_check[game_id] = {}, sender
    for client in get_connected_users(players_ids):
        shared.ready_check[game_id][0][client.jwtdata.id] = False
        await client.send(f"readycheck {game_name} {game_id}\r\n")

@UDPBroadcaster.register()
async def allready(sender, game_id, player_count):
    game = shared.games.get(game_id)
    if game is not None:
        game.readycnt += player_count
        if game.threshold == game.readycnt:
            game.ready_check_fail_future.cancel()
            asyncio.ensure_future(rungame(game_id))

@UDPBroadcaster.register()
async def readyfail(sender, game_id):
    game = shared.ready_check.get(game_id)
    if game is not None:
        await relay_to_players(sender,
                               game[0].keys(),
                               f"readyfail {game_id}\r\n");
        del shared.ready_check[game_id]


def main():
    """Main function called at script startup"""
    shared.manager_id = uuid4()
    shared.token = jwt.encode({
        "iss": "manager",
        "sub": "webgames",
        "iat": datetime.utcnow(),
        "type": "manager",
        "id": str(shared.manager_id),
        "name": str(shared.manager_id)[:6]
    }, JWT_SECRET)

    # Setup logging
    logging.root.level = logging.NOTSET
    stdout = logging.StreamHandler()
    stdout.level = LOG_LEVEL
    stdout.formatter = logging.Formatter(
        "{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{")
    logging.root.addHandler(stdout)

    logger.info("Manager ID is %s", shared.manager_id)

    # Setup asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # Setup SSL
    if USE_SSL:
        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sc.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)

    # Setup servers
    # TCP
    logger.info("Init %s TCP Server on %s:%d",
                "Secure" if USE_SSL else "Insecure",
                MANAGER_HOST,
                MANAGER_TCP_PORT)
    tcp_coro = asyncio.start_server(tcp_handler,
                                    MANAGER_HOST,
                                    MANAGER_TCP_PORT,
                                    ssl=sc if USE_SSL else None,
                                    loop=loop)
    tcp_server = loop.run_until_complete(tcp_coro)

    # WebSocket
    logger.info("Init %s WebSocket Server on %s:%d",
                "Secure" if USE_SSL else "Insecure",
                MANAGER_HOST,
                MANAGER_WS_PORT)
    ws_coro = websockets.serve(ws_handler,
                               MANAGER_HOST,
                               MANAGER_WS_PORT,
                               ssl=sc if USE_SSL else None,
                               loop=loop)
    ws_server = loop.run_until_complete(ws_coro)

    # Setup clients
    # Redis
    logger.info("Connect to %s Redis Server at %s:%d on database %d %s password",
                "Secure" if USE_SSL else "Insecure",
                REDIS_HOST,
                REDIS_PORT,
                REDIS_DB_MANAGER,
                "without" if REDIS_PASSWORD is None else "with")
    redis_coro = create_redis((REDIS_HOST, REDIS_PORT),
                              db=REDIS_DB_MANAGER,
                              password=REDIS_PASSWORD,
                              loop=loop)
    shared.redis = loop.run_until_complete(redis_coro)

    # HTTP
    logger.info("Setup HTTP Client session")
    shared.http = ClientSession(json_serialize=ujson.dumps,
                                headers={
                                    "Authorization": "Bearer " + shared.token.decode()
                                }, loop=loop)
    async def get_queues():
        async with shared.http.get(API_URL + "/queue/actives") as resp:
            assert resp.status == 200
            shared.queues = await resp.json(loads=ujson.loads)
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
        kicking = [client.kick("Server is shutting down...", level=logging.DEBUG)
                   for client in shared.uid_to_client.values()]
        await asyncio.wait(kicking)
    if shared.uid_to_client:
        logger.info("Kicking clients...")
        loop.run_until_complete(kick_all_clients())

    logger.info("Shutting down servers")
    tcp_server.close()
    ws_server.close()
    shared.redis.close()
    shared.http.close()
    loop.run_until_complete(asyncio.wait([
        tcp_server.wait_closed(),
        ws_server.wait_closed(),
        shared.redis.wait_closed()
    ]))
    loop.close()

if __name__ == "__main__":
    main()

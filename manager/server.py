#!./venv/bin/python

from os import environ
import asyncio
import logging
import signal
import ssl

import aiohttp
import uvloop
import websockets

from clients_handler import ClientHandler
from config import *

logger = logging.getLogger(__name__)


async def tcp_handler(reader, writer):

    async def send(message: str):
        writer.send(message.encode())
        await writer.drain()

    def close():
        writer.close()

    client = ClientHandler(writer.get_extra_info("peername"), send, close)

    logger.info("New TCP connection from %s:%d", *client.peername)
    while True:
        try:
            data = await reader.read(65536).decode()
        except ConnectionResetError as e:
            if not client.closed:
                logger.warning("Connection reset by %s", str(client))
            break
        except:
            if not client.closed:
                logger.exception("Exception while reading data from %s.", str(client))
            break

        logger.debug("Message from %s: %s", str(client), msg)
        if msg == "":
            logger.warning("Empty payload from %s. Assume connection closed by peer", str(client))
            break

        await client.evaluate(msg)
        if client.closed:
            break
        
    writer.close()
    logger.info("Connection with %s closed", str(client))


async def ws_handler(ws, path):
    async def send(message: str):
        await ws.send(message)

    async def close():
        await ws.close()

    client = ClientHandler(ws.remote_address, send, close)

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

        await client.evaluate(data)
        if client.closed:
            break

    await ws.close()
    logger.info("Connection with %s closed", str(client))
            

def main():
    # Setup logging
    logging.root.level = logging.NOTSET
    stdout = logging.StreamHandler()
    stdout.level = LOG_LEVEL
    stdout.formatter =  logging.Formatter(
        "{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{")
    logging.root.addHandler(stdout)
    
    # Setup asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # Setup SSL
    if SSL:
        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sc.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)

    # Setup servers
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

from sys import exc_info
from websocket_server import WebsocketServer
import json
import logging
from logging.handlers import QueueHandler

from game_server.manager import Manager
from exceptions import *
from signal import signal, SIGTERM
from sys import exit

root = logging.getLogger()
root.setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)
manager = None


def term_handler(signum, _):
    logger.info("Recieved SIGTERM. Stopping")
    manager.safe_stop()
    exit(0)


def onconnect(client, server):
    """Handle incoming connections"""

    logger.info("Client ID %d connected from %s:%d.", client["id"], client["address"][0], client["address"][1])
    token = manager.connect(client)  # Add this client (client ID, client socket) to the manager
    server.send_message(client, json.dumps({"cmd": "connection_success", "id": client["id"], "token": token}))

def ondisconnect(client, server):
    """Handle disconnections"""

    if client:
        logger.info("Client ID %d disconnected.", client["id"])
        manager.disconnect(client["id"])  # Remove this client from the manager

def onmessage(client, server, message):
    """Handle incoming messages"""

    logger.debug("Message from client ID %d: %s", client["id"], message)
    try:
        dictmsg = json.loads(message)  # Try to parse the message

        assert isinstance(dictmsg, dict)
        assert "cmd" in dictmsg

        # Client want to send an event
        if dictmsg["cmd"] == "event":
            assert "event" in dictmsg and "kwargs" in dictmsg
            manager.send_event(client["id"], dictmsg["event"], **dictmsg["kwargs"])

        # Client want to join a queue
        elif dictmsg["cmd"] == "join_queue":
            assert "queue" in dictmsg
            manager.join_queue(client["id"], dictmsg["queue"])

    # Syntax, Grammatical or Semantic Error
    except (json.decoder.JSONDecodeError, AssertionError, GameServerException) as e:
        logger.warning("Client ID %d generated error %s with message %s", client["id"], repr(e), message)
        server.send_message(client, json.dumps({"cmd": "error", "error": repr(e)}))

def start(host, port, stored_id, queue):
    """Start both the Game Manager and the Web Server"""

    signal(SIGTERM, term_handler)

    for handler in root.handlers.copy():
        root.removeHandler(handler)

    root.addHandler(QueueHandler(queue))

    logger.info("Init Web-Socket Server")
    # Prepare the web server with above functions
    server = WebsocketServer(port, host)
    server.set_fn_new_client(onconnect)
    server.set_fn_client_left(ondisconnect)
    server.set_fn_message_received(onmessage)

    logger.info("Init Game Manager")
    global manager
    manager = Manager(server, stored_id)


    logger.info("Web-Socket server listening on ws://%s:%d", host, port)
    try:
        server.run_forever()
    except Exception as ex:
        logger.critical("Web-Socket server stopped working !", exc_info=ex)
        exit(1)

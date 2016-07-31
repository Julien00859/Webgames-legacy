from server.exceptions import *
from server.game_manager import Manager
from settings.server_settings import *
from sys import exc_info
from websocket_server import WebsocketServer
import json
import logging

logger = logging.getLogger(__name__)

manager = None

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
            assert "event" in dictmsg and "args" in dictmsg and "kwargs" in dictmsg
            manager.send_event(client["id"], dictmsg["event"], dictmsg["args"], dictmsg["kwargs"])

        # Client want to join a queue
        elif dictmsg["cmd"] == "join_queue":
            assert "queue" in dictmsg
            manager.join_queue(client["id"], dictmsg["queue"])

    # Syntax, Grammatical or Semantic Error
    except (json.decoder.JSONDecodeError, AssertionError, ProjectException) as e:
        logger.warning("Client ID %d generated error %s with message %s", client["id"], repr(e), message)
        server.send_message(client, json.dumps({"cmd": "error", "error": repr(e)}))

def start_server():
    """Start both the Game Manager and the Web Server"""

    # Prepare the web server with above functions
    logger.info("Init Web Socket Server")
    server = WebsocketServer(PORT, HOST)
    server.set_fn_new_client(onconnect)
    server.set_fn_client_left(ondisconnect)
    server.set_fn_message_received(onmessage)

    # Create a game manager
    logger.info("Init Game Manager")
    global manager
    manager = Manager(server)

    # Start the web server
    logger.info("Starting Server")
    server.run_forever()
    manager.safe_stop()

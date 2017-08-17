#!./venv/bin/python

"""TCP Client for testing the server"""

from socket import socket, timeout
from threading import Thread, Event
from contextlib import suppress
from sys import argv
from time import sleep

from config import MANAGER_HOST, MANAGER_TCP_PORT

class Client(Thread):
    """Interface for communicate with the server"""
    def __init__(self, jwt):
        """Initiate the socket and some event"""
        self.jwt = jwt
        self.socket = socket()
        self.socket.settimeout(1)
        Thread.__init__(self)
        self.stopevt = Event()
        self.connectedevt = Event()
        self.preparedcmd = ""

    def bye(self):
        """Send 'quit' command to the server and stop the loop"""
        self.send("quit")
        self.stopevt.set()

    def run(self):
        """Listen the socket"""
        self.stopevt.clear()
        self.connectedevt.clear()
        self.socket.connect((MANAGER_HOST, MANAGER_TCP_PORT))
        while not self.stopevt.is_set():
            with suppress(timeout):
                data = self.socket.recv(1024).decode()
                for line in data.splitlines():
                    print("< " + line)
                    cmd, args = line.split(" ", 1)
                    if cmd == "ping":
                        value = int(args)
                        print("> pong", value)
                        self.send("pong {}".format(value))
                        self.connectedevt.set()
                    elif cmd == "quit":
                        self.stopevt.set()
                    elif cmd == "readycheck":
                        self.preparedcmd = "ready " + args.split(" ")[1]
                        print(self.preparedcmd + " ? ")

        self.socket.close()
        print("Disconnected")

    def send(self, cmd):
        """Send a command to the server, include the JWT and the CRLF"""
        self.socket.send("{} {}\r\n".format(self.jwt, cmd).encode())

the_jwt = argv[1] if len(argv) >= 2 else input("JWT: ")

client = Client(the_jwt)
client.start()

print("Connecting...")
client.connectedevt.wait()
print("Connected")

while True:
    cli = input("> ")
    if client.stopevt.is_set():
        break
    if cli.split(" ")[0] == "quit":
        client.bye()
        break
    elif cli.casefold() == "y":
        client.send(client.preparedcmd)
    else:
        client.send(cli)
    sleep(5)

client.join()

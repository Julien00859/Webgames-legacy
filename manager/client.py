#!./venv/bin/python

from config import *

from socket import socket, timeout
from threading import Thread, Event
from contextlib import suppress
from sys import argv

class Client(Thread):
    def __init__(self, jwt):
        self.jwt = jwt
        self.socket = socket()
        self.socket.settimeout(1)
        Thread.__init__(self)
        self.stopevt = Event()
        self.connectedevt = Event()
    
    def quit(self):
        self.send("quit")
        self.stopevt.set()

    def run(self):
        self.stopevt.clear()
        self.connectedevt.clear()
        self.socket.connect((SERVER_HOST, SERVER_TCP_PORT))
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
        self.socket.close()
        print("Disconnected")

    def send(self, cmd):
        self.socket.send("{} {}\r\n".format(self.jwt, cmd).encode())
           
jwt = argv[1] if len(argv) >= 2 else input("JWT: ")

c = Client(jwt)
c.start()

print("Connecting...")
c.connectedevt.wait()
print("Connected")

while True:
    line = input("> ")
    if c.stopevt.is_set():
        break
    if line.split(" ")[0] == "quit":
        c.quit()
        break
    else:
        c.send(line)

c.join()

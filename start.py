#!venv/bin/python

from os import name as osname, getpid
from sys import version_info
from settings import *
from multiprocessing import Process, Queue
from logging import getLogger, NOTSET
from logging.handlers import QueueHandler
from signal import signal, sigwait, SIGTERM

import argparse


from log_server.log_server import start as log_server_start
from auth_server.auth_server import start as auth_server_start
#from game_server.game_server import start as game_server_start

def start():
    log_queue = Queue()

    root = getLogger()
    root.setLevel(NOTSET)
    root.addHandler(QueueHandler(log_queue))
    logger = getLogger(__name__)

    processes = [
        Process(target=log_server_start, args=(log_queue,)),
        Process(target=auth_server_start, args=(log_queue,))
        #Process(target=game_server_start, args=(log_queue,))
    ]


    logger.info("Server started with PID %d", getpid())

    for process in processes:
        logger.info("Start %s", repr(process))
        process.start()

    def stop(signum, _):
        for process in reversed(processes):
            logger.info("Terminate %s", repr(process))
            process.terminate()
            process.join()

    signal(SIGTERM, stop)

def createdb():
    from models import Session, Base, engine, User, Game
    from getpass import getpass
    from hashlib import sha256
    from game_server.game_finder import get_games

    s = Session()
    session = Session()
    Base.metadata.create_all(engine)

    admin = User(u_name=input("Admin name: "), u_email=input("Admin email: "), u_password=sha256(getpass("Admin password: ").encode()).hexdigest())

    games = []
    for name in get_games().keys():
        games.append(Game(g_name=name))

    session.add(admin)
    session.add_all(games)
    session.commit()
    exit(0)

if __name__ == "__main__":
    if osname != "posix":
        raise OSError("This program need to run on Linux")

    if version_info < PYTHON_REQUIRED_VERSION:
        raise EnvironmentError("This program need at least Python {}.{}. You're using Python {}.{}".format(*PYTHON_REQUIRED_VERSION, *version_info))

    parser = argparse.ArgumentParser(description="Start all WebGames server at once !")
    parser.add_argument("--createdb", action="store_true", help="Create the databases, insert default values and exit", dest="createdb")
    parsed = parser.parse_args()

    if parsed.createdb:
        createdb()
        exit(0)

    start()

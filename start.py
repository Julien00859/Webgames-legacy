#!venv/bin/python

from os import name as osname, getpid
from sys import version_info
from settings import *
from multiprocessing import Process, Queue
from logging import getLogger, NOTSET
from logging.handlers import QueueHandler
from signal import signal, sigwait, SIGTERM


from log_server.log_server import start as log_server_start
#from auth_server.auth_server import start as auth_server_start
#from game_server.game_server import start as game_server_start

def start():
    log_queue = Queue()

    root = getLogger()
    root.setLevel(NOTSET)
    root.addHandler(QueueHandler(log_queue))
    logger = getLogger(__name__)

    processes = [
        Process(target=log_server_start, args=(log_queue,))
        #Process(target=auth_server_start, args=(log_queue,)),
        #Process(target=game_server_start, args=(log_queue,))
    ]


    logger.info("Server started with PID %d", getpid())

    for process in processes:
        logger.info("Start %s", repr(process))
        process.start()

    def stop():
        fullexitcode = 0x0

        for process in reversed(processes):
            process.terminate()
            process.join()

            fullexitcode = (fullexitcode << 8) | (process.exitcode & 255)

        exit(fullexitcode)

    signal(SIGTERM, stop)

if __name__ == "__main__":
    if osname != "posix":
        raise OSError("This program need to run on Linux")

    if version_info < PYTHON_REQUIRED_VERSION:
        raise EnvironmentError("This program need at least Python {}.{}. You're using Python {}.{}".format(*PYTHON_REQUIRED_VERSION, *version_info))


    start()

#!venv/bin/python

from os import name as osname
from settings import *
from multiprocessing import Process, Queue


from log_server.log_server import start as log_server_start
from auth_server.auth_server import start as auth_server_start
from game_server.game_server import start as game_server_start

def start():
    log_queue = Queue()
    processes = [
        Process(target=log_server_start, args=(log_queue,)),
        Process(target=auth_server_start, args=(log_queue,)),
        Process(target=game_server_start, args=(log_queue,)),
    ]

    def stop(signnum, _):
        """Stop all the servers by sending them SIGTERM and exit"""

        fullexitcode = 0x0

        for process in reversed(processes):
            process.terminate()
            process.join()

            fullexitcode = (fullexitcode << 8) | (process.exitcode & 255)

        exit(fullexitcode)

    signal(SIGTERM, stop)

    for process in processes:
        process.start()

if __name__ == "__main__":
    if osname != "posix":
        raise OSError()

    start()

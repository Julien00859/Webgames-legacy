#!./venv/bin/python


from collections import namedtuple
from gzip import open as gzipopen
from itertools import count
from logging.handlers import QueueListener
from multiprocessing import Process, Queue as mpQueue
from os import  getcwd, mkdir, sep, getpid, name as osname
from os.path import exists, isdir, isfile, join as pathjoin
from queue import Queue as thQueue
from shutil import copyfileobj
from signal import signal, SIGTERM
from threading import Thread
import json
import logging
import sys

from auth_server.auth_server import start as auth_server_start
from game_server.game_server import start as game_server_start
from settings import *
import models

session = models.Session()
logger = logging.getLogger(__name__)

def term_handler(signum, _):
    logger.info("Recieved SIGTERM. Stopping servers...")
    for server in servers:
        logger.info("Sending SIGNTEM to %s", server)
        server.terminate()
        server.join()

    logger.info("Done. Stopping QueueListener")
    queue_listener.enqueue_sentinel()
    logging.shutdown()

def chroot():
    if CHROOT_TO_PROJECT_DIR:
        if osname == "posix":
            from os import chroot
            try:
                chroot(getcwd())
                logger.info("Chroot to %s", getcwd())
            except PermissionError as ex:
                logger.error("Cannot chroot", exc_info=ex)
        else:
            logger.warning("Chroot is not available for your system.")

def setup_logs() -> mpQueue:
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    handlers = []

    if LOG_TO_CONSOLE:
        # Config the console logging
        console = logging.StreamHandler()
        console.setLevel(getattr(logging, LOG_CONSOLE_LEVEL))
        console.setFormatter(logging.Formatter("[{levelname}] <{name}> {message}", style="{"))
        root.addHandler(console)
        handlers.append(console)

    if LOG_TO_FILE:

        # If the `keep_log` option is set to true, compress the log file and name
        # it after the date and time of the first entry of the log file
        # > latest.log => yyyy-mm-dd_hh-mm-ss.gz
        if KEEP_LOG:
            if not isdir(LOG_DIR):
                mkdir(LOG_DIR)

            if exists(LOG_FILE_NAME) and isfile(LOG_FILE_NAME):
                # Fetch the first line, get the date and time, join them with an "_"
                # and finaly change ":" and "/" to "-"
                datetime = "_".join(open(LOG_FILE_NAME, "r").readline().split(" ")[:2]).replace(":","-").replace("/","-")

                # Compress the log file to the new file
                with open(LOG_FILE_NAME, 'rb') as f_in:
                    with gzipopen(pathjoin(LOG_DIR, datetime + ".gz"), 'wb') as f_out:
                        copyfileobj(f_in, f_out)            


        # Config the file logging
        file = logging.FileHandler(pathjoin(LOG_DIR, LOG_FILE_NAME), "w")
        file.setLevel(getattr(logging, LOG_FILE_LEVEL))
        file.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
        root.addHandler(file)
        handlers.append(file)

    if LOG_TO_DB:
        # Config the SQL logging
        db = SQLAlchemyHandler(session)
        db.setLevel(getattr(logging, LOG_DB_LEVEL))
        root.addHandler(db)
        handlers.append(db)


    if not any([LOG_TO_CONSOLE, LOG_TO_FILE, LOG_TO_DB]):
        # If no handler has been set, disable logging
        nowhere = logging.NullHandler()
        root.addHandler(nowhere)
        handlers.append(nowhere)

    logger.info("Logging initialized")

    queue = mpQueue()
    queue_listener = QueueListener(queue, *handlers, respect_handler_level=True)
    queue_listener.start()
    logger.info("QueueListener now handle sub-precesses log records")

    return queue

def start_servers():

    servers = []
    if START_AUTH_SERVER:
        server.append(Process(target=auth_server_start, args=(queue)))

    if START_GAME_SERVER:
        servers.append(Process(target=game_server_start, args=(queue)))

    for server in servers:
        logger.info("Starting %s", server)
        server.start()


signal(SIGTERM, term_handler)
logger.info("Server running on PID %d. Send SIGTERM (aka kill) to terminate.", getpid())

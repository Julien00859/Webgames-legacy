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
from sqlalchemy import create_engine
from threading import Thread
import json
import logging
import sys

from auth_server.auth_server import start as auth_server_start
from game_server.game_server import start as game_server_start
from settings import *
import models


class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        if not hasattr(record, "message"):
            record.message = self.format(record)
        if not hasattr(record, "playerid"):
            record.playerid = None
        if not hasattr(record, "gameid"):
            record.gameid = None

        models.session.add(models.Log(
            created=record.created,
            exc_text=record.exc_text,
            filename=record.filename,
            levelname=record.levelname,
            levelno=record.levelno,
            lineno=record.lineno,
            module=record.module,
            message=record.message,
            pathname=record.pathname,
            playerid=record.playerid,
            gameid=record.gameid
        ))


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def term_handler(signum, _):
    logger.info("Recieved SIGTERM. Stopping servers...")
    for server in servers:
        logger.info("Sending SIGNTEM to %s", server)
        server.terminate()
        server.join()

    logger.info("Done. Stopping QueueListener")
    queue_listener.enqueue_sentinel()
    logging.shutdown()

# =====================================================================================

# Store message until the logging is ready
LogEntry = namedtuple("LogEntry", ("lvl", "msg", "args", "kwargs"))
tolog = []




# Check if we must chroot
if CHROOT_TO_PROJECT_DIR:
    if osname == "posix":
        from os import chroot
        try:
            chroot(getcwd())
            tolog.append(LogEntry(lvl="INFO", 
                                  msg="Chroot to %s",
                                  args=[getcwd()],
                                  kwargs={}))

        except PermissionError as e:
            tolog.append(LogEntry(lvl="WARNING", 
                                  msg="Couldn't chroot. %s", 
                                  args=[str(e)], 
                                  kwargs={}))
    else:
        tolog.append(LogEntry(lvl="WARNING",
                              msg="Chroot is not available for your system (\"%s\" instead of \"posix\"), please consider setting CHROOT_TO_PROJECT_DIR to False in your server settings",
                              args=[osname],
                              kwargs={}))

# Init logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
handlers = []

# Config the console logging
if LOG_TO_CONSOLE:
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, LOG_CONSOLE_LEVEL))
    console.setFormatter(logging.Formatter("[{levelname}] <{name}> {message}", style="{"))
    logger.addHandler(console)
    handlers.append(console)
    tolog.append(LogEntry(lvl="INFO",
                          msg="Console logging initialized",
                          args=[],
                          kwargs={}))

# Check for logs dir
if not isdir(LOG_DIR):
    tolog.append(LogEntry(lvl="WARNING",
                          msg="Logs directory not found, creating a new one at .%s%s%s",
                          args=[sep, LOG_DIR, sep],
                          kwargs={}))
    mkdir(LOG_DIR)

# File logging
if LOG_TO_FILE:

    # If the `keep_log` option is set to true, compress the log file and name
    # it after the date and time of the first entry of the log file
    # > latest.log => yyyy-mm-dd_hh-mm-ss.gz
    if KEEP_LOG:

        # Get the log file
        if exists(LOG_FILE_NAME):
            if not isfile(LOG_FILE_NAME):
                raise OSError("LOG_FILE_NAME exists but isn't a correct file. Please check its value is the server settings.")

            # Fetch the first line, get the date and time, join them with an "_"
            # and finaly change ":" and "/" to "-"
            datetime = "_".join(open(LOG_FILE_NAME, "r").readline().split(" ")[:2]).replace(":","-").replace("/","-")

            tolog.append(LogEntry(lvl="INFO",
                                  msg="GZip previous log file \"%s\" to \"%s\"",
                                  args=[LOG_FILE_NAME, datetime + ".gz"],
                                  kwargs={}))

            # Compress the log file to the new file
            with open(LOG_FILE_NAME, 'rb') as f_in:
                with gzipopen(pathjoin(LOG_DIR, datetime + ".gz"), 'wb') as f_out:
                    copyfileobj(f_in, f_out)

    # Config the file logging
    file = logging.FileHandler(pathjoin(LOG_DIR, LOG_FILE_NAME), "w")
    file.setLevel(getattr(logging, LOG_FILE_LEVEL))
    file.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
    logger.addHandler(file)
    handlers.append(file)
    tolog.append(LogEntry(lvl="INFO",
                          msg="File logging initialized",
                          args=[],
                          kwargs={}))

# Config the db logging
if LOG_TO_DB:
    db = SQLAlchemyHandler()
    db.setLevel(getattr(logging, LOG_DB_LEVEL))
    logger.addHandler(db)
    handlers.append(db)
    tolog.append(LogEntry(lvl="INFO",
                          msg="Database logging initialized",
                          args=[],
                          kwargs={}))


# If no handler has been set, disable logging
if not any([LOG_TO_CONSOLE, LOG_TO_FILE, LOG_TO_DB]):
    logger.addHandler(logging.NullHandler)


# Logging is now initialized so we send all stored messages
for lvl, msg, args, kwargs in tolog:
    logger.log(getattr(logging, lvl), msg, *args, **kwargs)


if LOG_STDOUT:
    sys.stdout = StreamToLogger(logging.getLogger("stdout"))

if LOG_STDERR:
    sys.stderr = StreamToLogger(logging.getLogger("stderr"))

queue = mpQueue()

queue_listener = QueueListener(queue, *handlers, respect_handler_level=True)
queue_listener.start()

logger.info("QueueListener ready to handle sub-precesses log records")

gameid = models.session.query(models.StoredId).filter(models.StoredId.name == "gameid").one().storedid
logger.debug(gameid)

# Launch the servers
servers = [
    Process(
        target=auth_server_start,
        args=(AUTH_HOST, AUTH_PORT, SSL_CERT_PATH, SSL_KEY_PATH, queue)
    ),
    Process(
        target=game_server_start,
        args=(WS_HOST, WS_PORT, gameid, queue)
    )
]

for server in servers:
    logger.info("Starting %s", server)
    server.start()


signal(SIGTERM, term_handler)
logger.info("Server running on PID %d. Send SIGTERM (aka kill) to terminate.", getpid())

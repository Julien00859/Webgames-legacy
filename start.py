#!./venv/bin/python

if __name__ != "__main__":
    raise ImportError("This startup script may not provide any useful API")

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
import pickle
import sqlite3
import sys

from auth_server.auth_server import start as auth_server_start
from game_server.game_server import start as game_server_start
from settings import *

class SQLiteHandler(logging.Handler, Thread):
    """Logging handler for the SQLite3 database"""

    create_statement = """CREATE TABLE IF NOT EXISTS log (
                              id int primary key,
                              created real,
                              exc_text text,
                              filename text,
                              funcName text,
                              levelname text,
                              levelno int,
                              lineno int,
                              module text,
                              message text,
                              name text,
                              pathname text,
                              playerid int,
                              gameid int
                        );"""

    insert_statement = """INSERT INTO log (
                              id,
                              created,
                              exc_text,
                              filename,
                              funcName,
                              levelname,
                              levelno,
                              lineno,
                              module,
                              message,
                              name,
                              pathname,
                              playerid,
                              gameid
                        )
                        VALUES (
                              :id,
                              :created,
                              :exc_text,
                              :filename,
                              :funcName,
                              :levelname,
                              :levelno,
                              :lineno,
                              :module,
                              :message,
                              :name,
                              :pathname,
                              :playerid,
                              :gameid
                        );"""

    def __init__(self, database, stored_id):
        logging.Handler.__init__(self)
        Thread.__init__(self)

        # Save the args
        self.database = database

        # Retrieve the ID
        self.logid = count(stored_id)

        # Create a queue with a sentinel
        self.queue = thQueue()
        self.sentinel = object()

        # Prevent the thread from blocking the exit
        self.daemon = True

        # Start the thread
        self.start()

    # override logging.Handler.emit
    def emit(self, record):
        """Feed the queue with a record"""

        if not hasattr(record, "message"):
            record.message = self.format(record)

        if not hasattr(record, "playerid"):
            record.playerid = None

        if not hasattr(record, "gameid"):
            record.gameid = None

        record.id = next(self.logid)

        self.queue.put(record)

    # override logging.Handler.close
    def close(self):
        """Feed the queue with the sentinel and wait for the thread to stop"""

        self.queue.put(self.sentinel)
        self.join()

        # Save the stored_id
        data = pickle.load(open("data", "rb"))
        data["stored_ids"]["log"] = next(self.logid)
        pickle.dump(data, open("data", "wb"))

    def run(self):
        """Consume the queue to insert the records in the database"""

        # Connect to db and create the table if it doesn't exists
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute(self.create_statement)

        # Main loop
        while True:
            # Get a record or the sentinel
            record = self.queue.get()

            # If it's the sentinel, exit loop, commit and close db
            if record is self.sentinel:
                break

            # Otherwise insert the record into the table
            cur.execute(self.insert_statement, record.__dict__)
            self.queue.task_done()

        cur.close()
        conn.commit()
        conn.close()
        self.queue.task_done()


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


# Get the data
if isfile("data"):
    data = pickle.load(open("data", "rb"))
else:
    tolog.append(LogEntry(lvl="WARNING",
                          msg="Data file not found, creating a new one at ./data",
                          args=(),
                          kwargs={}))
    data = {
        "stored_ids": {
            "log": 1,
            "game": 1
        }
    }
    pickle.dump(data, open("data", "wb"))

tolog.append(LogEntry(lvl="DEBUG", 
                      msg="Stored datas are: %s",
                      args=data,
                      kwargs={}))


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
    if not isfile(pathjoin(LOG_DIR, LOG_DB_NAME)):
        tolog.append(LogEntry(lvl="WARNING",
                              msg="Logs database not found, creating a new one at .%s%s%s%s",
                              args=[sep, LOG_DIR, sep, LOG_DB_NAME],
                              kwargs={}))    

    db = SQLiteHandler(pathjoin(LOG_DIR, LOG_DB_NAME), data["stored_ids"]["log"])
    db.setLevel(getattr(logging, LOG_DB_LEVEL))
    logger.addHandler(db)
    handlers.append(db)
    tolog.append(LogEntry(lvl="INFO",
                          msg="Database logging initialized",
                          args=[],
                          kwargs={}))


# If no handler has been set, disable logging
if not any([LOG_TO_CONSOLE, LOG_DB_LEVEL, LOG_TO_DB]):
    logger.addHandler(logging.NullHandler)


# Logging is now initialized so we send all stored messages
for lvl, msg, args, kwargs in tolog:
    logger.log(getattr(logging, lvl), msg, *args, **kwargs)

queue = mpQueue()

queue_listener = QueueListener(queue, *handlers, respect_handler_level=True)
queue_listener.start()

logger.info("QueueListener ready to handle sub-precesses log records")


# Launch the servers
servers = [
    Process(
        target=auth_server_start,
        args=(AUTH_HOST, AUTH_PORT, SSL_CERT_PATH, SSL_KEY_PATH, queue)
    ),
    Process(
        target=game_server_start,
        args=(WS_HOST, WS_PORT, data["stored_ids"]["game"], queue)
    )
]

for server in servers:
    logger.info("Starting %s", server)
    server.start()


signal(SIGTERM, term_handler)
logger.info("Server running on PID %d. Send SIGTERM (aka kill) to terminate.", getpid())

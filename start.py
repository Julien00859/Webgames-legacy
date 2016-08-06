#!./venv/bin/python

if __name__ != "__main__":
    raise ImportError("This startup script may not provide any useful API")

from collections import namedtuple
from gzip import open as gzipopen
from os import  getcwd, mkdir, sep, name as osname
from os.path import basename, exists, isdir, isfile, join as pathjoin
from shutil import copyfileobj
from sqlite_handler.sqlite_handler import SQLiteHandler
from time import strftime
import json
import logging
import sqlite3
import sys

from game_server.server import start_server
from game_server.settings import *


class LogFile(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, name=None):
        self.logger = logging.getLogger(name)

    def write(self, msg, level=logging.INFO):
        if msg.strip():
            self.logger.log(level, msg.strip())

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

# Store message until the logging is ready
LogEntry = namedtuple("LogEntry", ("lvl", "msg", "args", "kwargs"))
tolog = []

conn = sqlite3.connect("main.db")
cur = conn.cursor()
for name, count in cur.execute("select name, count from counters").fetchall():
    if name == "log_id":
        stored_log_id = count
    elif name == "game_id":
        stored_game_id = count
conn.close()


# Check if we must chroot
if CHROOT_TO_PROJECT_DIR:
    if osname == "posix":
        from os import chroot
        try:
            chroot(getcwd())
            tolog.append(LogEntry(lvl="INFO", msg="Chroot to %s", args=[getcwd()], kwargs={}))

        except PermissionError as e:
            tolog.append(LogEntry(lvl="WARNING", msg="Couldn't chroot. %s", args=[str(e)], kwargs={}))
    else:
        tolog.append(LogEntry(
            lvl="WARNING",
            msg="Chroot is not available for your system (\"%s\" instead of \"posix\"), please consider setting CHROOT_TO_PROJECT_DIR to False in your server settings",
            args=[osname],
            kwargs={})
        )
        

# Check for logs dir
if not isdir("logs"):
    tolog.append(LogEntry(lvl="WARNING", msg="Logs directory not found, creating a new one at .%s%s%s%s%s", args=[sep, basename(getcwd()), sep, "logs", sep], kwargs={}))
    mkdir("logs")

logging.basicConfig(
    level=getattr(logging, LOG_CONSOLE_LEVEL),
    format="[{levelname}] <{name}> {message}",
    style="{",
    datefmt="%Y/%m/%d %X"
)

if LOG_TO_FILE:
    log_path = pathjoin("logs", LOG_FILE_NAME)  # Create a path to the log file

    # If the `keep_log` option is set to true, compress the `log_path` file and name
    # it after the date and time of the first entry of the log file
    # > latest.log => yyyy-mm-dd_hh-mm-ss.gz
    if KEEP_LOG:
        if exists(log_path):
            if not isfile(log_path):
                raise OSError("LOG_FILE exists but isn't a correct file. Please check its value is the server settings.")

            # Fetch the first line, get the date and time, join them with an "_"
            # and finaly change ":" and "/" to "-"
            datetime = "_".join(open(log_path, "r").readline().split(" ")[:2]).replace(":","-").replace("/","-")

            tolog.append(LogEntry(lvl="INFO", msg="GZip previous log file \"%s\" to \"%s\"", args=[LOG_FILE_NAME, datetime + ".gz"], kwargs={}))

            with open(log_path, 'rb') as f_in:
                with gzipopen(pathjoin("logs", datetime + ".gz"), 'wb') as f_out:
                    copyfileobj(f_in, f_out)

    file = logging.FileHandler(log_path, "w")
    file.setLevel(getattr(logging, LOG_FILE_LEVEL))
    file.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
    logging.getLogger("").addHandler(file)

if LOG_TO_DB:
    db = SQLiteHandler(pathjoin("logs", LOG_DB_NAME), stored_log_id)
    db.setLevel(getattr(logging, LOG_DB_LEVEL))
    db.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
    logging.getLogger("").addHandler(db)

logging.info("Logging initialized")

# Logging is now initialized so we send all stored messages
for lvl, msg, args, kwargs in tolog:
    logging.log(getattr(logging, lvl), msg, *args, **kwargs)

# Redirect stdout to logging
#sys.stdout = LogFile('sys.stdout')

# Launch the server
try:
    start_server(stored_game_id)

except Exception as e:
    logging.critical("Fatal unhandled error ! %s", repr(e), exc_info=e)

finally:
    sys.stdout = sys.__stdout__
    logging.info("Exiting")
    logging.shutdown()
    
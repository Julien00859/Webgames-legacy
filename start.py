# Do not import this file
if __name__ != "__main__":
    raise ImportError("This startup script may not provide any useful API")

from collections import namedtuple
from gzip import open as gzipopen
from os import  getcwd, mkdir, sep, name as osname
from os.path import basename, exists, isdir, isfile, join as pathjoin
from shutil import copyfileobj
from time import strftime
import logging
import sqlite3
import sys

from server.web_server import start_server
from settings.server_settings import *


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
    tolog.append(LogEntry(lvl="WARNING", msg="Logs directory not found, creating a new one at %s%s%s%s", args=[basename(getcwd()), sep, "logs", sep], kwargs={}))
    mkdir("logs")

log_path = pathjoin("logs", LOG_FILE)  # Create a path to the log file

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

        tolog.append(LogEntry(lvl="INFO", msg="GZip previous log file \"%s\" to \"%s\"", args=[LOG_FILE, datetime + ".gz"], kwargs={}))

        with open(log_path, 'rb') as f_in:
            with gzipopen(pathjoin("logs", datetime + ".gz"), 'wb') as f_out:
                copyfileobj(f_in, f_out)

# File logging configuration
logging.basicConfig(
    filename=log_path,
    level=getattr(logging, FILE_LEVEL),
    format="{asctime} {levelname:<8} {name:<20} {message}",
    style="{",
    datefmt="%Y/%m/%d %X",
    filemode="w"
)
# Console logging configuration (same but skip the date/time)
console = logging.StreamHandler()
console.setLevel(getattr(logging, CONSOLE_LEVEL))
console.setFormatter(logging.Formatter("[{levelname}] <{name}> {message}", style="{"))
logging.getLogger("").addHandler(console)

logging.info("Logging initialized")

# Logging is now initialized so we send all stored messages
for lvl, msg, args, kwargs in tolog:
    logging.log(getattr(logging, lvl), msg, *args, **kwargs)

# If Database type is "sqlite" then check for database file to exists
if DB_TYPE == "sqlite":
    if exists(DB_SQLITE_FILE) and not isfile(DB_SQLITE_FILE):
        raise OSError("DB_SQLITE_FILE exists but isn't a correct file. Please check its value is the server settings.")

    # If not, creating a new one with a given schema
    elif not exists(DB_SQLITE_FILE):
        logging.warning("Database not found, creating a new one at %s", pathjoin(basename(getcwd()), DB_SQLITE_FILE))
        conn = sqlite3.connect(DB_SQLITE_FILE)
        cur = conn.cursor()
        cur.executescript(open(pathjoin("settings", "schema.sql"), "r").read())
        conn.commit()
        conn.close()

# Redirect stdout and stderr to logging
sys.stdout = LogFile('sys.stdout')
sys.stderr = LogFile('sys.stderr')

# Launch the server
try:
    start_server()
    exitcode = 0

except Exception as e:
    logging.critical("Fatal unhandled error ! %s", repr(e), exec_info=e)
    exitcode = 1

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

logging.info("Exiting with exit code %d", exitcode)
logging.shutdown()

sys.exit(exitcode)
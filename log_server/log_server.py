import logging
from logging.handlers import QueueListener, QueueHandler
from multiprocessing import Queue
from typing import List
from os.path import getmtime, join as pathjoin, isdir, isfile, dirname
from os import mkdir
from datetime import datetime
from signal import signal, SIGTERM
from gzip import open as gzipopen
from shutil import copyfileobj

from settings import *
from models import Session
from utils.handlers import *


def get_console_handler() -> logging.Handler:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_CONSOLE_LEVEL)
    console_handler.setFormatter(logging.Formatter("[{levelname}] <{name}> {message}", style="{"))
    return console_handler


def get_file_handler() -> logging.Handler:
    file_handler = logging.FileHandler(pathjoin(dirname(__file__), LOG_FILE_DIR, LOG_FILE_NAME), "w")
    file_handler.setLevel(LOG_FILE_LEVEL)
    file_handler.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
    return file_handler


def get_sql_handler() -> logging.Handler:
    sql_handler = SQLAlchemyHandler(Session())
    sql_handler.setLevel(LOG_SQL_LEVEL)
    return sql_handler


def timetostring(seconds: int):
    """Convert seconds to string according to a format suitable for a filename (no "/" or ":")
    @param seconds: seconds since epoch
    @return "year-month-day_hour-minute-second"""

    return datetime.fromtimestamp(seconds).strftime("%y-%m-%d_%H-%M-%S")


def compress(filein: str, fileout: str) -> None:
    """Compress a file using GZIP and store it at another location
    @param filein: the path of the file that will be compressed
    @param fileout: the path where to store the compressed file"""

    with open(filein, 'rb') as f_in:
        with gzipopen(fileout, 'wb') as f_out:
            copyfileobj(f_in, f_out)


def start(log_queue: Queue) -> QueueListener:
    root = logging.getLogger()

    logger = logging.getLogger(__name__)
    handlers = []

    if LOG_CONSOLE:
        logger.info("Add console handler")
        handlers.append(get_console_handler())

    log_dir_path = pathjoin(dirname(__file__), LOG_FILE_DIR)
    log_file_path = pathjoin(log_dir_path, LOG_FILE_NAME)

    if not isdir(log_dir_path):
        mkdir(log_dir_path)

    if LOG_FILE:
        if LOG_FILE_STORE and isfile(log_file_path):
            logger.info("Backup previous log file")
            compress(log_file_path, pathjoin(log_dir_path, timetostring(getmtime(log_file_path))))
        logger.info("Add file handler")
        handlers.append(get_file_handler())

    if LOG_SQL:
        logger.info("Add SQL handler")
        handlers.append(get_sql_handler())

    root.removeHandler(root.handlers[0])  # Retire le QueueHandler
    if handlers:
        for handler in handlers:
            root.addHandler(handler)
    else:
        root.addHandler(logging.NullHandler())

    queue_listener = QueueListenerNoThread(log_queue, *handlers, respect_handler_level=True)

    def stop(signnum, _) -> None:
        """Stop the process by stopping the QueueListener and the logging module"""

        logger.info("Stop QueueListener")
        queue_listener.stop()
        logging.shutdown()
        exit(0)
    signal(SIGTERM, stop)

    logger.info("Start QueueListener")
    queue_listener.start()

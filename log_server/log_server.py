import logging
from logging.handlers import QueueListener
from typing import List
from os.path import getmtime, join as pathjoin
from datetime import datetime
from signal import signal, SIGTERM

from settings import *


def add_console_handler(root: logging.Logger, handlers: List[logging.Handler]) -> None:
	"""Add a console handler to the root logger
	@param root: the root logger this handler will be attached at
	@param handlers: the full list of handlers"""

	console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_CONSOLE_LEVEL))
    console_handler.setFormatter(logging.Formatter("[{levelname}] <{name}> {message}", style="{"))
    root.addHandler(console_handler)
	handlers.append(console_handler)


def add_file_handler(root: logging.Logger, handlers: List[logging.Handler]) -> None:
	"""Add a file handler to the root logger
	@param root: the root logger this handler will be attached at
	@param handlers: the full list of handlers"""

    file_handler = logging.FileHandler(pathjoin(LOG_DIR, LOG_FILE_NAME), "w")
    file_handler.setLevel(getattr(logging, LOG_FILE_LEVEL))
    file_handler.setFormatter(logging.Formatter("{asctime} [{levelname}] <{name}> {message}", style="{"))
    root.addHandler(file_handler)
	handlers.append(file_handler)


def add_sql_handler(root: logging.Logger, handlers: List[logging.Handler]) -> None:
	"""Add a SQL handler to the root logger
	@param root: the root logger this handler will be attached at
	@param handlers: the full list of handlers"""

	sql_handler = SQLAlchemyHandler(session)
    sql_handler.setLevel(getattr(logging, LOG_DB_LEVEL))
    root.addHandler(sql_handler)
	handlers.append(sql_handler)


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


def start(log_queue: multiprocessing.Queue): QueueListener
	root = logging.getLogger()
	root.setLevel(logging.NOTSET)
	handlers = []

	if LOG_CONSOLE:
		add_console_logger(root, handlers)

	if LOG_FILE:
		if LOG_FILE_STORE:
			compress(pathjoin(LOG_FILE_DIR, LOG_FILE_NAME), pathjoin(LOG_FILE_DIR, timetostring(getmtile(LOG_FILE_NAME))))
		add_file_logger(root, handlers)

	if LOG_SQL:
		add_sql_logger(root, handlers)

	if not any(LOG_CONSOLE, LOG_FILE, LOG_SQL):
		root.addHandler(logging.NullHandler())

	
	queue_listener = QueueListener(log_queue, *handlers, respect_handler_level=True)

	def stop(signnum, _) -> None:
		"""Stop the process by stopping the QueueListener and the logging module"""

		queue_listener.enqueue_sentinel()
		queue_listener.stop()
		logging.shutdown()
		exit(0)
	signal(SIGTERM, stop)

	queue_listener.start()
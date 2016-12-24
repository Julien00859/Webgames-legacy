from wrapt import synchronized
from typing import Dict
from datetime import datetime
from threading import Lock
from settings import AUTH_TOKEN_EXPIRATION

tokens = {}
lock = Lock()

@synchronized(lock)
def add_token(token: str) -> None:
	tokens[token] = datetime.utcnow() + AUTH_TOKEN_EXPIRATION

@synchronized(lock)
def isvalid_token(token: str) -> bool:
	if token not in tokens:
		return False

	if tokens[token] > datetime.utcnow():
		remove(token)
		return False

	return True

@synchronized(lock)
def remove_token(token: str) -> None:
	del tokens[token]
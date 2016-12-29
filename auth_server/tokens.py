from binascii import hexlify
from collections import namedtuple
from datetime import datetime, timedelta
from itertools import islice, cycle
from os import urandom
from threading import RLock

from settings import AUTH_TOKEN_EXPIRATION, AUTH_TOKEN_LENGTH, AUTH_TOKEN_GENERATION_MAX_TRY

Infos = namedtuple("Infos", ["userid", "expiration"])

class Tokens:
	def __init__(self):
		self.tokens = {}
		self.lock = RLock()
		self.free_indice = 0  # Used to cycle the free method

	def create(self, userid: int) -> str:
		"""Generate a new random token. This method is thread-safe
		@param userid : the id of the token owner
		@return : a new token
		@throws RuntimeError : the generation failed after x tries"""

		with self.lock:
			for x in range(AUTH_TOKEN_GENERATION_MAX_TRY):
				token = hexlify(urandom(AUTH_TOKEN_LENGTH)).decode()
				if token not in self.tokens:
					self.tokens[token] = Infos(userid, datetime.utcnow() + AUTH_TOKEN_EXPIRATION)
					return token
			else:
				raise RuntimeError("Could not generate a new token")

	def refresh(self, token: str) -> None:
		"""Reset the expiration of a token. This method is thread-safe
		@param token : the token to refresh
		@throws ValueError : the token wasn't found"""
		with self.lock:
			if token in self.tokens:
				self.tokens[token].expiration = datetime.utcnow() + AUTH_TOKEN_EXPIRATION
			else:
				raise ValueError("Could not refresh that token")

	def remove(self, token: str) -> None:
		"""Remove a token. This method is thread-safe
		@param token : the token to remove
		@throws ValueError : the token wasn't found"""

		with self.lock:
			if token in self.tokens:
				del self.tokens[token]
			else:
				raise ValueError("Could not delete that token")

	def isvalid(self, token: str) -> bool:
		"""Validate a token. This method is thread-safe
		@param token : the token to validate
		@return : True if the token exists and is not expirated, False otherwise"""

		with self.lock:
			expiration = self.tokens.get(token)

			if expiration is None:
				return False

			elif expiration < datetime.utcnow():
				if self.lock_update.acquire(blocking=False):
					del self.tokens[token]
					self.lock_update.release()
				return False
			
			return True

	def free(self, timeout:timedelta=None) -> None:
		"""Free expirated tokens. This method is thread-safe"""

		with self.lock:
			tokens = self.tokens.copy()

			now = datetime.utcnow()
			for n, token, exp in map(lambda n, t: (n, t[0], t[1].expiration), islice(enumerate(cycle(tokens.copy().items())), self.free_indice, len(tokens) + self.free_indice)):
				if exp > now:
					del tokens[token]
				if timeout is not None and n % 1024 == 0 and now + timeout > datetime.utcnow():
					self.free_indice += n
					break

			self.tokens = tokens

	def remove_user(self, userid: int) -> None:
		"""Remove all tokens used by an user. This method is thread-safe
		@param userid : the id of the user"""

		with self.lock:
			tokens = self.tokens.copy()
			now = datetime.utcnow()

			for token, uid in map(lambda t, i: (t, i.userid), tokens.copy().items()):
				if uid == userid:
					del self.tokens[token]

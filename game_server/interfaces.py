from abc import ABCMeta, abstractmethod
from itertools import count
from settings import GAME_FREQUENCY


class Game(metaclass=ABCMeta):
	frequency = GAME_FREQUENCY
	gameid = 0
	players = {}
	tickgen = count()
	is_over = False

	@abstractmethod
	def __init__(self, game_id: int, players: list):
		pass

	@abstractmethod
	def start(self, *args, **kwargs) -> Status:
		pass

	@abstractmethod
	def get_events(self, player_id) -> list:
		pass
	
	@abstractmethod
	def run_event(self, player_id: int, event_name: str, **kwargs) -> None:
		pass

	@abstractmethod
	def kill(self, player_id) -> None:
		pass


class Status(metaclass=ABCMeta):
	didsmthhappen = False
	tickno = 0
	winners = []

	@abstractmethod
	def __init__(self, tickno: int):
		pass

	@abstractmethod
	def set_winners(self, winner: list) -> None:
		pass

	@abstractmethod
	def to_dict(self) -> dict:
		pass

	@abstractmethod
	def __str__(self) -> str:
		pass


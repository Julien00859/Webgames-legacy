from importlib import import_module
from inspect import getmro
from logging import getLogger
from os import walk, listdir
from os.path import join as pathjoin, isdir, isfile, dirname, sep

from game_server.interfaces import Game
from settings import GAMES_DIR

logger = getLogger(__name__)

def get_games():
	"""Go deep into the game folder to find all the classes that extends the interface Game
	@return a dict with queue name as key and game class as value"""

	games = {}

	games_path = pathjoin("game_server", GAMES_DIR)
	for dir_ in listdir(games_path):

		game_path = pathjoin(games_path, dir_)
		if isdir(game_path):
			for file in listdir(game_path):
				file_path = pathjoin(game_path, file)
				if isfile(file_path) and file.endswith(".py"):
					try:
						module = import_module(file_path[:-3].replace(sep, "."))
					except:
						logger.exception("Could not load module at %s", file_path)
					else:
						for s in dir(module):
							class_ = getattr(module, s)
							if type(class_) == type(Game) and class_ != Game:
								if Game in getmro(class_):
									games[dir_] = class_;

	return games

if __name__ == "__main__":
	print(get_games())
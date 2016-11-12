class WebGames(BaseException):
    pass

class AuthServerException(WebGames):
	pass

class GameServerException(WebGames):
	pass

class ManagerException(GameServerException):
	pass

class AlreadyRegistered(ManagerException):
	pass

class ClientAlive(ManagerException):
	pass

class InGame(ManagerException):
	pass

class InvalidEvent(ManagerException):
	pass

class InvalidMessage(ManagerException):
	pass

class InvalidQueue(ManagerException):
	pass

class InvalidToken(ManagerException):
	pass

class NotInGame(ManagerException):
	pass

class NotRegistered(ManagerException):
	pass

class ServerStopping(ManagerException):
	pass

class GameException(GameServerException):
	pass
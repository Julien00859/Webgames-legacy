class ProjectException(BaseException):
    pass

class AlreadyRegistered(ProjectException):
	pass

class ClientAlive(ProjectException):
	pass

class InGame(ProjectException):
	pass

class InvalidEvent(ProjectException):
	pass

class InvalidMessage(ProjectException):
	pass

class InvalidQueue(ProjectException):
	pass

class InvalidToken(ProjectException):
	pass

class NotInGame(ProjectException):
	pass

class NotRegistered(ProjectException):
	pass

class ServerStopping(ProjectException):
	pass
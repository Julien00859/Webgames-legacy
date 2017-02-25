from logging import Handler

class SQLAlchemyHandler(Handler):
    def __init__(self, dbsession):
        super().__init__()
        self.dbsession = dbsession

    def emit(self, record):
        if not hasattr(record, "message"):
            record.message = self.format(record)
        if not hasattr(record, "playerid"):
            record.playerid = None
        if not hasattr(record, "gameid"):
            record.gameid = None

        self.dbsession.add(models.Log(
            created=record.created,
            exc_text=record.exc_text,
            filename=record.filename,
            levelname=record.levelname,
            levelno=record.levelno,
            lineno=record.lineno,
            module=record.module,
            message=record.message,
            pathname=record.pathname,
            playerid=record.playerid,
            gameid=record.gameid
        ))
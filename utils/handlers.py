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
        if not hasattr(record, "tickno"):
            record.tickno = None

        self.dbsession.add(models.Log(**record))
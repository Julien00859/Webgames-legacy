from logging import Handler
from logging.handlers import QueueListener
from models import Log

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

        self.dbsession.add(Log(
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

class QueueListenerNoThread(QueueListener):
    def __init__(self, queue, *handlers, respect_handler_level):
        self.queue = queue
        self.handlers = handlers
        self.respect_handler_level = respect_handler_level

    def start(self):
        has_task_done = hasattr(self.queue, 'task_done')
        while True:
            try:
                record = super().dequeue(True)
                if record is self._sentinel:
                    break
                self.handle(record)
                if has_task_done:
                    self.queue.task_done()
            except:
                break        

    def stop(self):
        super().enqueue_sentinel()
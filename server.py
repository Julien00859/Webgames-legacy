import asyncio
from datetime import timedelta, datetime
import logging
from gzip import open as gzipopen
from os.path import join as pathjoin, isfile, isdir, getmtime
from os import mkdir
from shutil import copyfileobj
from pytimeparse import parse as timeparse
from sanic import Sanic
from sanic_compress import Compress
import uvloop
import accounts
import challenges
import database as db
from routes import router

def start(addr: str, port: int, domain: str, schemessl: bool, pwdsalt: str,
          dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str,
          smtphost: str, smtpport: int, smtpuser: str, smtppwd: str, smtpssl: bool,
          redishost: str, redisport: int, redispwd: str, redisdb: int, redispoolsize: int,
          logstdout: bool, logstdoutlevel: str, logstdoutformat: str,
          logfile: bool, logfilelevel: str, logfileformat: str,
          logfilename: str, logfilearchive: bool,
          tklength: int, tkvalidity: str, chlglength: int, chlgvalidity: str):

    # Set package constant
    accounts.token_length = tklength
    accounts.token_validity = timedelta(seconds=timeparse(tkvalidity)).total_seconds()
    challenges.challenge_length = chlglength
    challenges.challenge_validity = timedelta(seconds=timeparse(chlgvalidity)).total_seconds()
    db.salt = pwdsalt

    # Init logs
    logging.root.level = logging.NOTSET
    if logstdout:
        stdout = logging.StreamHandler()
        stdout.level = getattr(logging, logstdoutlevel)
        stdout.formatter = logging.Formatter(logstdoutformat, style="{")
        logging.root.addHandler(stdout)

    if logfile:
        if not isdir("logs"):
            mkdir("logs")
        logpath = pathjoin("logs", logfilename)
        if logfilearchive and isfile(logpath):
            archivepath = pathjoin("logs", datetime.fromtimestamp(getmtime(logpath)).strftime("%y-%m-%d_%H-%M-%S") + ".gz")  # RIP PEP8
            with open(logpath, 'rb') as f_in:
                with gzipopen(archivepath, 'wb') as f_out:
                    copyfileobj(f_in, f_out)

        file = logging.FileHandler(logpath, "w")
        file.level = getattr(logging, logfilelevel)
        file.formatter = logging.Formatter(logfileformat, style="{")
        logging.root.addHandler(file)

    if not any([logstdout, logfile]):
        logging.root.addHandler(logging.NullHandler())



    # Init web server
    app = Sanic(__name__)

    Compress(app)

    app.config.domain = domain
    app.config.schemessl = schemessl
    app.config.smtphost = smtphost
    app.config.smtpport = smtpport
    app.config.smtpuser = smtpuser
    app.config.smtppwd = smtppwd
    app.config.smtpssl = smtpssl

    # Init http and ws routes
    router(app)

    # Connect to database and cache
    app.add_task(db.connect_to_db(host=dbhost, port=dbport, user=dbuser,
                                  database=dbname, password=dbpwd))
    app.add_task(db.connect_to_cache(host=redishost, port=redisport, db=redisdb,
                                     password=redispwd, poolsize=redispoolsize))

    # Start web server
    app.run(host=addr, port=port)

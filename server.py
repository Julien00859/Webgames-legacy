import asyncio
from datetime import timedelta, datetime
import logging
from gzip import open as gzipopen
from os.path import join as pathjoin, isfile, getmtime
from shutil import copyfileobj
from pytimeparse import parse as timeparse
from sanic import Sanic
from sanic_compress import Compress
import uvloop
import accounts
import challenges
import database as db
import views

def start(addr: str, port: int, domain: str, schemessl: bool, pwdsalt: str,
          dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str,
          smtphost: str, smtpport: int, smtpuser: str, smtppwd: str, smtpssl: bool,
          logstdout: bool, logstdoutlevel: str, logstdoutformat: str,
          logfile: bool, logfilelevel: str, logfileformat: str,
          logfilename: str, logfilearchive: bool,
          tklength: int, tkvalidity: str, chlglength: int, chlgvalidity: str):

    # Set package constant
    accounts.token_length = tklength
    accounts.token_validity = timedelta(seconds=timeparse(tkvalidity))
    challenges.challenge_length = chlglength
    challenges.challenge_validity = timedelta(seconds=timeparse(chlgvalidity))
    db.salt = pwdsalt

    # Init logs
    logging.root.level = logging.NOTSET
    if logstdout:
        stdout = logging.StreamHandler()
        stdout.level = getattr(logging, logstdoutlevel)
        stdout.formatter = logging.Formatter(logstdoutformat, style="{")
        logging.root.addHandler(stdout)

    if logfile:
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

    app.add_task(db.connect(host=dbhost, port=dbport, user=dbuser,
                            database=dbname, password=dbpwd))

    app.add_route(views.index, "/", methods=["GET"])
    app.add_route(views.signup, "/signup", methods=["POST"])
    app.add_route(views.signin, "/signin", methods=["POST"])
    app.add_route(views.refresh, "/refresh", methods=["POST"])
    app.add_route(views.signout, "/signout", methods=["POST"])
    app.add_route(views.challenge, "/challenge/<token>", methods=["GET"])
    app.static("/assets", pathjoin(".", "client", "assets"))

    # Start web server
    app.run(host=addr, port=port)

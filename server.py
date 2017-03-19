import asyncio
from datetime import timedelta
import logging
from os.path import join as pathjoin
from pytimeparse import parse as timeparse
from sanic import Sanic
import uvloop
import accounts
import challenges
import database as db
import views

def start(addr: str, port: int, domain: str, schemessl: bool,
          dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str,
          pwdsalt: str, loglevel: str,
          tklength: int, tkvalidity: str,
          chlglength: int, chlgvalidity: str) -> None:

    # Set package constant
    accounts.token_length = tklength
    accounts.token_validity = timedelta(seconds=timeparse(tkvalidity))
    challenges.challenge_length = chlglength
    challenges.challenge_validity = timedelta(seconds=timeparse(chlgvalidity))
    db.salt = pwdsalt

    # Init logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s",
        level=getattr(logging, loglevel))

    # Init web server
    app = Sanic(__name__)
    app.config.domain = domain
    app.config.schemessl = schemessl

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

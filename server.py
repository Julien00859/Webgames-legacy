from os.path import join as pathjoin
from datetime import timedelta
import logging
from sanic import Sanic
from pytimeparse import parse as timeparse
import views
import accounts
import database as db
import challenges
import asyncio
import uvloop

def start(addr: str, port: int, dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str, pwdsalt: str, loglevel: str, tklength: int, tkvalidity: str, chlglength: int, chlgvalidity: str, chlgurl: str) -> None:
    accounts.token_length = tklength
    accounts.token_validity = timedelta(seconds=timeparse(tkvalidity))
    challenges.challenge_length = chlglength
    challenges.challenge_validity = timedelta(seconds=timeparse(chlgvalidity))
    challenges.challenge_url = chlgurl
    db.salt = pwdsalt

    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s", level=getattr(logging, loglevel))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.connect(dbhost, dbport, dbuser, dbname, dbpwd, loop))

    app = Sanic(__name__)

    app.add_route(views.index, "/", methods=["GET"])
    app.add_route(views.signup, "/signup", methods=["POST"])
    app.add_route(views.signin, "/signin", methods=["POST"])
    app.add_route(views.refresh, "/refresh", methods=["POST"])
    app.add_route(views.signout, "/signout", methods=["POST"])
    app.add_route(views.challenge, "/challenge/<token>", methods=["GET"])
    app.static("/assets", pathjoin(".", "client", "assets"))

    app.run(host=addr, port=port, loop=loop)

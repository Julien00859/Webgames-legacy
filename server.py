import asyncio
import uvloop
from aiohttp import web
import aiohttp_jinja2
import jinja2
from functools import partial
import logging
from os import getcwd
from os.path import join as pathjoin
from pytimeparse import parse as timeparse
from datetime import timedelta
import socketio import AsyncServer

import accounts
from routes import setup_routes
import database

def start(addr: str, port: int, dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str, loglevel: str, tklength: int, tkvalidity: str, pwdsalt: str) -> None:
    accounts.token_len = tklength
    accounts.token_validity = timedelta(seconds=timeparse(tkvalidity))
    database.salt = pwdsalt

    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s", level=getattr(logging, loglevel))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    app = web.Application(loop=loop)
    setup_routes(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(""))
    app.router.add_static("/assets/", path=pathjoin(getcwd(), "assets"), name="assets")

    loop.run_until_complete(database.connect(dbhost, dbport, dbuser, dbname, dbpwd, loop))
    web.run_app(app, host=addr, port=port)

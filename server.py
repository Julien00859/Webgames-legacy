import asyncio
import uvloop
from aiohttp import web
import aiohttp_jinja2
import jinja2
from functools import partial
import logging
from os import getcwd
from os.path import join as pathjoin

from routes import setup_routes
from database import connect as dbconnect

def start(addr: str, port: int, ssl: bool, dbhost: str, dbport: int, dbuser: str, dbname: str, dbpwd: str, loglevel: str) -> None:
    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s", level=getattr(logging, loglevel))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    app = web.Application(loop=loop)
    setup_routes(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))
    app.router.add_static("/static/", path=pathjoin(getcwd(), "static"), name="static")

    loop.run_until_complete(dbconnect(dbhost, dbport, dbuser, dbname, dbpwd, loop))
    web.run_app(app, host=addr, port=port)

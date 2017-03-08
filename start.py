#!./venv/bin/python

from argparse import ArgumentParser
from sys import argv, version_info
import asyncio
import logging
from collections import namedtuple

from settings import *
from server import start
from database import connect, create

version = namedtuple("version", ["major", "minor", "micro", "releaselevel"])(3, 0, 0, "alpha")

parser = ArgumentParser(description="Management script")
parser.add_argument("action", choices=["runserver", "createdb"])
parser.add_argument("-V", "--version", action="version", version="WebGames {app.major}.{app.minor}.{app.micro}-{app.releaselevel} (Python {py.major}.{py.minor}.{py.micro}-{py.releaselevel})".format(app=version, py=version_info))
action = parser.parse_args(argv[1:2]).action

if action == "runserver":
    parser = ArgumentParser(description="Start script", prog=" ".join(argv[0:2]))
    parser.add_argument("-a", "--addr", action="store", default=WGHOST, help="host address")
    parser.add_argument("-p", "--port", action="store", type=int, default=WGPORT, help="host port")
    parser.add_argument("--dbhost", action="store", default=PGHOST, help="database host address")
    parser.add_argument("--dbport", action="store", default=PGPORT, help="connection port number")
    parser.add_argument("--dbuser", action="store", default=PGUSER, help="name of the database role used for authentication")
    parser.add_argument("--dbpwd", action="store", default=PGPASSWORD, help="password used for authentication")
    parser.add_argument("--dbname", action="store", default=PGDATABASE, help="database name")
    parser.add_argument("--loglevel", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default=LOGLEVEL, help="verbosity level")
    parser.add_argument("--tklength", action="store", type=int, default=TOKENLENGTH, help="token length")
    parser.add_argument("--tkvalidity", action="store", default=TOKENVALIDITY, help="token validity")
    parser.add_argument("--pwdsalt", action="store", type=bytes, default=PWDSALT, help="password salt")
    cli = parser.parse_args(argv[2:])
    start(**cli.__dict__)

elif action == "createdb":
    parser = ArgumentParser(description="Start script", prog=" ".join(argv[0:2]))
    parser.add_argument("--dbhost", action="store", default=PGHOST, help="database host address")
    parser.add_argument("--dbport", action="store", default=PGPORT, help="connection port number")
    parser.add_argument("--dbuser", action="store", default=PGUSER, help="name of the database role used for authentication")
    parser.add_argument("--dbpwd", action="store", default=PGPASSWORD, help="password used for authentication")
    parser.add_argument("--dbname", action="store", default=PGDATABASE, help="database name")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="print output")
    cli = parser.parse_args(argv[2:])

    loop = asyncio.get_event_loop()
    async def coro():
        if cli.verbose:
            print("Connect to databse")
        conn = await connect(cli.dbhost, cli.dbport, cli.dbuser, cli.dbname, cli.dbpwd, loop)
        if cli.verbose:
            print("Connected, create tables")
        await create()
        if cli.verbose:
            print("Tables created, close connection")
        await conn.close()
        if cli.verbose:
            print("Done.")

    loop.run_until_complete(coro())

#!./venv/bin/python

from argparse import ArgumentParser
from sys import argv, version_info
import asyncio
import logging
from collections import namedtuple
from os import environ

from yaml import load as yaml_load

from server import start
from database import connect, create

version = namedtuple("version", ["major", "minor", "micro", "releaselevel"])(3, 0, 0, "alpha")

parser = ArgumentParser(description="Management script")
parser.add_argument("action", choices=["runserver", "initdb"])
parser.add_argument("-V", "--version", action="version", version="WebGames {app.major}.{app.minor}.{app.micro}-{app.releaselevel} (Python {py.major}.{py.minor}.{py.micro}-{py.releaselevel})".format(app=version, py=version_info))
action = parser.parse_args(argv[1:2]).action
settings = yaml_load(open("settings.yml", "r"))

if action == "runserver":
    parser = ArgumentParser(description="Start script", prog=" ".join(argv[0:2]))
    parser.add_argument("-a", "--addr", action="store", default=environ.get("WGHOST", settings["webgames"]["host"]), help="host address")
    parser.add_argument("-p", "--port", action="store", type=int, default=int(environ.get("WGPORT", settings["webgames"]["port"])), help="host port")
    parser.add_argument("--dbhost", action="store", default=environ.get("PGHOST", settings["postgres"]["host"]), help="database host address")
    parser.add_argument("--dbport", action="store", default=environ.get("PGPORT", settings["postgres"]["port"]), help="connection port number")
    parser.add_argument("--dbuser", action="store", default=environ.get("PGUSER", settings["postgres"]["user"]), help="role used for authentication")
    parser.add_argument("--dbpwd", action="store", default=environ.get("PGPASSWORD", settings["postgres"]["password"]), help="password used for authentication")
    parser.add_argument("--dbname", action="store", default=environ.get("PGDATABASE", settings["postgres"]["database"]), help="database name")
    parser.add_argument("--pwdsalt", action="store", type=bytes, default=environ.get("PGSALT", settings["postgres"]["salt"]).encode("UTF-8"), help="password salt")
    parser.add_argument("--loglevel", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default=environ.get("WGLOGLEVEL", settings["log"]["level"]), help="verbosity level")
    parser.add_argument("--tklength", action="store", type=int, default=int(environ.get("WGTKLENGTH", settings["token"]["length"])), help="token length")
    parser.add_argument("--tkvalidity", action="store", default=environ.get("WGTKVALIDITY", settings["token"]["validity"]), help="token time validity")
    parser.add_argument("--chlglength", action="store", type=int, default=int(environ.get("WGCHLGLENGTH", settings["challenge"]["length"])), help="challenge length")
    parser.add_argument("--chlgvalidity", action="store", default=environ.get("WGCHLGVALIDITY", settings["challenge"]["validity"]), help="challenge time validity")
    parser.add_argument("--chlgurl", action="store", default=environ.get("WGCHLGURL", settings["challenge"]["url"]), help="challenge url")
    cli = parser.parse_args(argv[2:])
    start(**cli.__dict__)

elif action == "initdb":
    parser = ArgumentParser(description="Start script", prog=" ".join(argv[0:2]))
    parser.add_argument("--dbhost", action="store", default=environ.get("PGHOST", settings["postgres"]["host"]), help="database host address")
    parser.add_argument("--dbport", action="store", default=environ.get("PGPORT", settings["postgres"]["port"]), help="connection port number")
    parser.add_argument("--dbuser", action="store", default=environ.get("PGUSER", settings["postgres"]["user"]), help="name of the database role used for authentication")
    parser.add_argument("--dbpwd", action="store", default=environ.get("PGPASSWORD", settings["postgres"]["password"]), help="password used for authentication")
    parser.add_argument("--dbname", action="store", default=environ.get("PGDATABASE", settings["postgres"]["database"]), help="database name")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="print output")
    cli = parser.parse_args(argv[2:])

    print(cli.__dict__)

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

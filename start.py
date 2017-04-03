#!./venv/bin/python

from argparse import ArgumentParser
from sys import argv, version_info
import asyncio
import logging
from collections import namedtuple
from os import environ

from yaml import load as yaml_load

from server import start
import database as db

version = namedtuple("version", ["major", "minor", "micro", "releaselevel"])(3, 0, 0, "alpha")

parser = ArgumentParser(description="Management script")
parser.add_argument("action", choices=["runserver", "initdb"])
parser.add_argument("-V", "--version", action="version", version="WebGames {app.major}.{app.minor}.{app.micro}-{app.releaselevel} (Python {py.major}.{py.minor}.{py.micro}-{py.releaselevel})".format(app=version, py=version_info))
action = parser.parse_args(argv[1:2]).action
settings = yaml_load(open("settings.yml", "r"))

if action == "runserver":
    parser = ArgumentParser(description="Start script", prog=" ".join(argv[0:2]))
    parser.add_argument("-a", "--addr", action="store", default=environ.get("WG_HOST", settings["webgames"]["host"]), help="host address")
    parser.add_argument("-p", "--port", action="store", type=int, default=int(environ.get("WG_PORT", settings["webgames"]["port"])), help="host port")
    parser.add_argument("--domain", action="store", default=environ.get("WG_DOMAIN", settings["webgames"]["domain"]), help="domain name")
    parser.add_argument("--schemessl", action="store_true", default=bool(environ.get("WG_SCHEMESSL", settings["webgames"]["schemessl"])), help="build URL with HTTPS and WSS")
    parser.add_argument("--dbhost", action="store", default=environ.get("PGHOST", settings["postgres"]["host"]), help="database host address")
    parser.add_argument("--dbport", action="store", default=environ.get("PGPORT", settings["postgres"]["port"]), help="connection port number")
    parser.add_argument("--dbuser", action="store", default=environ.get("PGUSER", settings["postgres"]["user"]), help="role used for authentication")
    parser.add_argument("--dbpwd", action="store", default=environ.get("PGPASSWORD", settings["postgres"]["password"]), help="password used for authentication")
    parser.add_argument("--dbname", action="store", default=environ.get("PGDATABASE", settings["postgres"]["database"]), help="database name")
    parser.add_argument("--smtphost", action="store", default=environ.get("SMTP_HOST", settings["smtp"]["host"]), help="smtp host address")
    parser.add_argument("--smtpport", action="store", type=int, default=environ.get("SMTP_PORT", settings["smtp"]["port"]), help="smtp post")
    parser.add_argument("--smtpuser", action="store", default=environ.get("SMTP_USER", settings["smtp"]["user"]), help="email address used for authentication")
    parser.add_argument("--smtppwd", action="store", default=environ.get("SMTP_PASSWORD", settings["smtp"]["password"]), help="password used for authentication")
    parser.add_argument("--smtpssl", action="store_true", default=bool(environ.get("SMTP_SSL", settings["smtp"]["ssl"])), help="use smtp over ssl")
    parser.add_argument("--redishost", action="store", default=environ.get("REDIS_HOST", settings["redis"]["host"]), help="redis host address")
    parser.add_argument("--redisport", action="store", type=int, default=environ.get("REDIS_PORT", settings["redis"]["port"]), help="redis post")
    parser.add_argument("--redispwd", action="store", default=environ.get("REDIS_PASSWORD", settings["redis"]["password"]), help="password used for authentication")
    parser.add_argument("--redisdb", action="store", type=int, default=environ.get("REDIS_DATABASE", settings["redis"]["db"]), help="redis database number for webgames")
    parser.add_argument("--redisdbsio", action="store", type=int, default=environ.get("REDIS_DATABASE_SIO", settings["redis"]["dbsio"]), help="redis database number for socketio")
    parser.add_argument("--redispoolsize", action="store", type=int, default=environ.get("REDIS_POOLSIZE", settings["redis"]["poolsize"]), help="redis concurrent connection pool size")
    parser.add_argument("--pwdsalt", action="store", default=environ.get("PGSALT", settings["postgres"]["salt"]).encode("UTF-8"), help="password salt")
    parser.add_argument("--logstdout", action="store_true", default=bool(environ.get("WG_LOG_STDOUT", settings["log"]["stdout"]["enabled"])), help="log to stdout")
    parser.add_argument("--logstdoutlevel", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default=environ.get("WG_LOG_STDOUT_LEVEL", settings["log"]["stdout"]["level"]), help="verbosity level for stdout")
    parser.add_argument("--logstdoutformat", action="store", default=environ.get("WG_LOG_STDOUT_FORMAT", settings["log"]["stdout"]["format"]), help="log format for stdout")
    parser.add_argument("--logfile", action="store_true", default=bool(environ.get("WG_LOG_FILE", settings["log"]["file"]["enabled"])), help="log to file")
    parser.add_argument("--logfilelevel", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default=environ.get("WG_LOG_FILE_LEVEL", settings["log"]["file"]["level"]), help="verbosity level for file output")
    parser.add_argument("--logfileformat", action="store", default=environ.get("WG_LOG_FILE_FORMAT", settings["log"]["file"]["format"]), help="log format for file output")
    parser.add_argument("--logfilename", action="store", default=environ.get("WG_LOG_FILE_NAME", settings["log"]["file"]["name"]), help="log file name")
    parser.add_argument("--logfilearchive", action="store_true", default=bool(environ.get("WG_LOG_FILE_ARCHIVE", settings["log"]["file"]["archive"])), help="archive previous log file")
    parser.add_argument("--tklength", action="store", type=int, default=int(environ.get("WG_TKLENGTH", settings["token"]["length"])), help="token length")
    parser.add_argument("--tkvalidity", action="store", default=environ.get("WG_TKVALIDITY", settings["token"]["validity"]), help="token time validity")
    parser.add_argument("--chlglength", action="store", type=int, default=int(environ.get("WG_CHLGLENGTH", settings["challenge"]["length"])), help="challenge length")
    parser.add_argument("--chlgvalidity", action="store", default=environ.get("WG_CHLGVALIDITY", settings["challenge"]["validity"]), help="challenge time validity")
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
        conn = await db.connect_to_db(cli.dbhost, cli.dbport, cli.dbuser, cli.dbname, cli.dbpwd)
        if cli.verbose:
            print("Connected, create tables")
        await db.create()
        if cli.verbose:
            print("Tables created, close connection")
        await conn.close()
        if cli.verbose:
            print("Done.")

    loop.run_until_complete(coro())

#!./venv/bin/python
from aioredis import create_redis
from asyncpg import connect as pg_connect
from sanic import Sanic
from sanic.response import text
from config import WEBAPI_HOST, WEBAPI_PORT, JWT_SECRET, LOG_LEVEL,\
                   REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD,\
                   POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
import asyncio
import logging
from uuid import uuid4
import jwt as jwtlib
from datetime import datetime
import shared
from auth import auth_bp
from functools import partial, partialmethod

logger = logging.getLogger(__name__)
shared.app = Sanic()
shared.webapi_id = uuid4()
shared.token = jwtlib.encode({
    "iss": "webapi",
    "sub": "webgames",
    "iat": datetime.utcnow(),
    "type": "webapi",
    "tid": str(uuid4()),
    "id": str(shared.webapi_id),
}, JWT_SECRET)


shared.app.blueprint(auth_bp)

@shared.app.route("/status")
async def status(req):
    return text("")

async def connect_to_db():
    logger.info("Connect to Redis Server at %s:%d on database %d %s password",
                REDIS_HOST,
                REDIS_PORT,
                REDIS_DB,
                "without" if REDIS_PASSWORD is None else "with")
    redis_coro = create_redis((REDIS_HOST, REDIS_PORT),
                              db=REDIS_DB,
                              password=REDIS_PASSWORD,
                              loop=shared.app.loop)
    
    logger.info("Connect to PostgreSQL Server at %s:%d on database %s with user %s %s password",
                POSTGRES_HOST,
                POSTGRES_PORT,
                POSTGRES_DB,
                POSTGRES_USER,
                "without" if POSTGRES_PASSWORD is None else "and")
    pg_coro = pg_connect(host=POSTGRES_HOST,
                         port=POSTGRES_PORT,
                         user=POSTGRES_USER,
                         password=POSTGRES_PASSWORD,
                         database=POSTGRES_DB,
                         loop=shared.app.loop)
    
    global clients
    shared.redis, shared.postgres = await asyncio.gather(redis_coro, pg_coro, loop=shared.app.loop)
    logger.info("Connected")

def start_server():
    # Setup logging
    logging.getLogger("sanic").propagate = False
    logging.getLogger("network").propagate = False
    logging.addLevelName(45, "SECURITY")
    logging.root.level = logging.NOTSET
    stdout = logging.StreamHandler()
    stdout.level = LOG_LEVEL
    stdout.formatter = logging.Formatter(
        "{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{")
    logging.root.addHandler(stdout)

    logger.info("WebAPI ID is %s", shared.webapi_id)

    shared.app.add_task(connect_to_db())
    shared.app.run(host=WEBAPI_HOST, port=WEBAPI_PORT)

if __name__ == "__main__":
    start_server()

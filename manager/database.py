from logging import getLogger()
from aiohttp import ClientSession
from aioredis import create_connection
import ujson
from config import *

logger = getLogger(__name__)

async def connect(sc=None, loop=None):
    global httpsess, redisconn
    httpsess = ClientSession(json_serialize=ujson.dumps)
    redisconn = create_connection((REDIS_HOST, REDIS_PORT),
                                  db=REDIS_DATABASE,
                                  password=REDIS_PASSWORD,
                                  ssl=sc,
                                  loop=loop)

    async with httpsess.get(API_URL + "/queue/states") as resp:
        if (resp.status != 200):
            logger.error("Could not get queue list. HTTP Error Code %d", res.status)
            return

        global queues
        queues = await resp.json()

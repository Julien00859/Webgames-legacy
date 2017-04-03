import asyncpg
from typing import NamedTuple, Union, NewType
from hashlib import sha256
from os.path import sep
import aioredis
from asyncio import sleep
from logging import getLogger

salt: bytes
Number = NewType("Number", str)
logger = getLogger(__name__)


class User:
    def __init__(self, id: Union[int, Number], name: str, email: str,
                 password: str, dirty: Union[int, Number] = 0):
        self.id = int(id)
        self.name = name
        self.email = email
        self.password = password
        self.dirty = int(dirty)

    @classmethod
    async def get_by_id(cls, user_id: int) -> Union["User", None]:
        with await cachepool as redis:
            user_cache = await redis.hgetall(f"users:{user_id}")
            if user_cache:
                return cls(**user_cache)
            else:
                return cls.get_by_query("SELECT * from users where u_id=$1", user_id)

    @classmethod
    async def get_by_login(cls, login: str) -> Union["User", None]:
        return await cls.get_by_query("SELECT * FROM tbusers WHERE u_name=$1 or u_email=$1", login)

    @classmethod
    async def get_by_name(cls, name: str) -> Union["User", None]:
        return await cls.get_by_query("SELECT * FROM tbusers WHERE u_name=$1", name)

    @classmethod
    async def get_by_email(cls, email: str) -> Union["User", None]:
        return await cls.get_by_query("SELECT * from tbusers WHERE u_email=$1", email)

    @classmethod
    async def get_by_query(cls, query: str, *args) -> Union["User", None]:
        stmt = await conn.prepare(query)
        row = await stmt.fetchrow(*args)

        if row is None:
            return None

        user = cls(row["u_id"], row["u_name"], row["u_email"], row["u_password"])

        with await cachepool as cache:
            user_cache = await cache.hgetall(f"users:{user.id}")
            if user_cache:
                return User(**user_cache)
            else:
                await cache.hmset_dict(f"users:{user.id}", user.__dict__)
                return user

    @staticmethod
    async def is_free(name: str, email: str) -> bool:
        stmt = await conn.prepare("SELECT u_id FROM tbusers WHERE u_name=$1 or u_email=$2")
        return await stmt.fetchrow(name, email) is None

    @classmethod
    async def create(cls, name: str, email: str, password: str) -> "User":
        async with conn.transaction():
            sql = "INSERT INTO tbusers (u_name, u_email, u_password) VALUES ($1, $2, $3) RETURNING u_id"
            stmt = await conn.prepare(sql)
            u_id = await stmt.fetchval(name, email, password)

        return cls(u_id, name, email, password)

    @staticmethod
    def hashpwd(password: str) -> str:
        return sha256(salt + password.encode()).hexdigest()


class Guest(NamedTuple):
    name: str
    email: str
    password: str


class Game(NamedTuple):
    name: str
    dirty: bool


class Score(NamedTuple):
    user: str
    game: str
    play_count: int
    play_time: int
    win_count: int
    dirty: bool


conn: asyncpg.connection
async def connect_to_db(host: str, port: int, user: str, database: str,
                        password: str, loop=None) -> asyncpg.connection:
    global conn
    conn = await asyncpg.connect(host=host, port=port, user=user,
                                 database=database, password=password)
    return conn


cachepool: aioredis.pool
async def connect_to_cache(host: str, port: int, password: str,
                           poolsize: int, db: int) -> aioredis.pool:
    global cachepool
    cachepool = await aioredis.create_pool((host, port), password=password,
                                           db=db, maxsize=poolsize,
                                           encoding="utf-8")
    return cachepool


async def create() -> None:
    sql = open("sql" + sep + "init.sql", "r").read()
    await conn.execute(sql)

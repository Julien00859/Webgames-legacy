import asyncpg
from typing import NamedTuple, Union
from hashlib import sha256
from os.path import sep

class User(NamedTuple):
    name: str
    email: str
    password: str


class Game(NamedTuple):
    name: str


class Score(NamedTuple):
    user: str
    game: str
    play_count: int
    play_time: int
    win_count: int


salt: bytes
def hashpwd(password: str) -> str:
    return sha256(salt + password.encode()).hexdigest()


conn: asyncpg.connection
async def connect(host: str, port: int, user: str,
                  database: str, password: str, loop) -> asyncpg.connection:
    global conn
    conn = await asyncpg.connect(host=host, port=port, user=user,
                                 database=database, password=password, loop=loop)
    return conn


async def create() -> None:
    sql = open("sql" + sep + "init.sql", "r").read()
    await conn.execute(sql)


async def get_user_by_login(login: str) -> Union[User, None]:
    return await _get_user("SELECT * FROM tbusers WHERE u_name=$1 or u_email=$1", login)


async def get_user_by_name(name: str) -> Union[User, None]:
    return await _get_user("SELECT * FROM tbusers WHERE u_name=$1", name)


async def get_user_by_email(email: str) -> Union[User, None]:
    return await _get_user("SELECT * from tbusers WHERE u_email=$1", email)


async def is_user_free(name: str, email: str) -> bool:
    sql = "SELECT * FROM tbusers WHERE u_name=$1 or u_email=$2"
    return await _get_user(sql, name, email) is None


async def _get_user(query: str, *args) -> Union[User, None]:
    stmt = await conn.prepare(query)
    row = await stmt.fetchrow(*args)

    if row is None:
        return None

    return User(row.u_name, row.u_email, row.u_password)


async def add_user(name: str, email: str, hashedpwd: str):
    async with conn.transaction():
        sql = "INSERT INTO users (name, mail, password) VALUES ($1, $2, $3)"
        await conn.execute(sql, name, email, hashedpwd)

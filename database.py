import asyncpg
from collections import namedtuple

User = namedtuple("User", ["name", "mail", "password"])
Game = namedtuple("Game", ["name"])
Score = namedtuple("Score", ["user_id", "game_id", "play_count", "play_time", "win_count"])

conn = None
async def connect(host: str, port: int, user: str, database: str, password: str, loop):
    global conn
    conn = await asyncpg.connect(host=host, port=port, user=user, database=database, password=password, loop=loop)
    return conn

async def create():
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id serial PRIMARY KEY,
            name char(24) NOT NULL UNIQUE,
            mail varchar(254) NOT NULL UNIQUE,
            password char(64) NOT NULL,

            CONSTRAINT valid_name CHECK (name ~ '^[[:graph:] ]{4,24}$'),
            CONSTRAINT valid_mail CHECK (mail ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        );
        CREATE TABLE IF NOT EXISTS games (
            game_id serial PRIMARY KEY,
            name char(24) NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS scores (
            user_id serial,
            game_id serial,
            play_count signedint NOT NULL,
            play_time interval SECOND NOT NULL,
            win_count signedint NULL,

            CONSTRAINT pk PRIMARY KEY (user_id, game_id),
            CONSTRAINT fk_user_id FOREIGN KEY (user_id)
                REFERENCES users
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            CONSTRAINT fk_game_id FOREIGN KEY (game_id)
                REFERENCES games
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );
    """)

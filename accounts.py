import database as db
import secrets
from datetime import datetime, timedelta
from typing import NewType


token_length: int
token_validity: int
IPAddress = NewType("IPAddress", str)
Token = NewType("Token", str)


async def register(user_id: int) -> Token:
    """Generate a new token for a user"""

    token = secrets.token_urlsafe(token_length)

    with await db.cachepool as cache:
        await cache.set(f"users:{user_id}:tokens:{token}", 1)
        await cache.expire(f"users:{user_id}:tokens:{token}", token_validity)

    return token


async def freeze(user_id: int, addr: IPAddress) -> datetime:
    """Freeze an account for a while"""

    with await db.cachepool as cache:
        count = await cache.incr(f"users:{user_id}:fails:{addr}:count")

        if count < 5:
            unlock = datetime.utcnow()
        elif count < 20:
            unlock = datetime.utcnow() + timedelta(seconds=(2**count))
        else:
            unlock = datetime.utcnow() + timedelta(days=1)

        await cache.set(f"users:{user_id}:fails:{addr}:unlock",
                       int(unlock.timestamp()))


async def unfreeze(user_id: int, addr: IPAddress) -> None:
    """Unfreeze an account"""

    with await db.cachepool as cache:
        await cache.delete(f"users:{user_id}:fails:{addr}:count")


async def is_frozen(user_id: int, addr: IPAddress) -> bool:
    """Check if this IP can access its account"""

    with await db.cachepool as cache:
        unlock = await cache.get(f"users:{user_id}:fails:{addr}:unlock")

    return unlock is not None and \
           datetime.fromtimestamp(unlock) > datetime.utcnow()


async def is_token_valid(user_id: int, token: Token) -> bool:
    """Check if the token is valid"""
    
    with await db.cachepool as cache:
        return await cache.exists(f"users:{user_id}:tokens:{token}")


async def invalidate_token(user_id: int, token: Token) -> None:
    """Make a token invalid"""

    with await db.cachepool as cache:
        await cache.delete(f"users:{user_id}:tokens:{token}")

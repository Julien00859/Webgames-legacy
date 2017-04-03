import database as db
from datetime import datetime, timedelta
from typing import NewType
from secrets import token_urlsafe


challenge_length: int
challenge_validity: int
Challenge = NewType("Challenge", str)
IPAddress = NewType("IPAddress", str)


async def create_for(guest: db.Guest) -> Challenge:
    """Create a challenge for a db.Guest"""

    chlg = token_urlsafe(challenge_length)
    with await db.cachepool as cache:
        await cache.hmset_dict(f"chlgs:{chlg}", guest._asdict())
        await cache.expire(f"chlgs:{chlg}", challenge_validity)
    return chlg


async def solve(chlg: Challenge) -> bool:
    """Try to solve a challenge, if it does so: save the db.Guest in the db"""

    with await db.cachepool as cache:
        guest = await cache.hgetall(f"chlgs:{chlg}")
        if guest:
            await db.User.create(**guest)
            await cache.delete(f"chlgs:{chlg}")
            return True
        return False


async def freeze(addr: IPAddress) -> datetime:
    """Freeze an address for a while"""

    with await db.cachepool as cache:
        count = await cache.hincr(f"chlgtries:{addr}", "count")
        unlock = datetime.utcnow() + timedelta(seconds=30 * 2 ** count)
        await cache.hmset(f"chlgtries:{addr}", "unlock", unlock.total_seconds())

    return unlock


async def unfreeze(addr: IPAddress) -> None:
    """Unfreeze an address"""

    with await db.cachepool as cache:
        await cache.delete(f"chlgtries:{addr}")


async def is_frozen(addr: IPAddress) -> bool:
    """Check if the address is frozen"""

    with await db.cachepool as cache:
        unlock = await cache.get(f"fails:{addr}:unlock")

    return unlock is not None and \
           datetime.fromtimestamp(unlock) > datetime.utcnow()

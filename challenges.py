from typing import NewType, NamedTuple, Dict
from secrets import token_urlsafe
from database import User, add_user as db_add_user
from datetime import datetime, timedelta


IPAddress = NewType("IPAddress", str)

ChallengeToken = NewType("ChallengeToken", str)

class Try(NamedTuple):
    count: int
    lock_until: datetime

class ChallengeFor(NamedTuple):
	user: User
	expiration: datetime


tries: Dict[IPAddress, Try] = {}
challenges: Dict[ChallengeToken, ChallengeFor] = {}


challenge_length: int
challenge_validity: timedelta

def create_for(user: User) -> ChallengeToken:
	challenge = token_urlsafe(challenge_length)
	expiration = datetime.now() + challenge_validity

	challenges[challenge] = ChallengeFor(user, expiration)

	return challenge


async def solve(challenge: ChallengeToken) -> None:
	chlgfor = challenges.get(challenge)
	if chlgfor is None:
		return False

	if chlgfor.expiration < datetime.now():
		del challenges[challenge]
		return False

	await db_add_user(*chlgfor.user)
	del challenges[challenge]
	return True


def fail(addr: IPAddress):
	if addr not in tries:
		tries[addr] = Try(count=0, lock_until=datetime.now())

	else:
		tries[addr].count += 1

		time = 30 * 2 ** account[user_id].tries[addr].count
		tries[addr].lock_until = datetime.now() + timedelta(seconds=time)

	return tries[addr].lock_until


def is_locked(addr: IPAddress) -> bool:
	return addr in tries and datetime.now() < tries[addr].lock_until

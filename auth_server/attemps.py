from wrapt import synchronized
from threading import Lock
from datetime import datetime, timedelta
from collections import namedtuple

Infos = namedtuple("Infos", ["count", "last_try"])

attemps = {}
lock = Lock()


@synchronized(lock)
def incr(login: str, address: str):
	if login not in attemps:
		attemps[login] = {
			address: Infos(count=1, last_try=datetime.utcnow())
		}

	elif address not in attemps[login]:
		attemps[login][address] = Infos(count=1, last_try=datetime.utcnow())

	else:
		attemps[login][address].count += 1
		attemps[login][address].last_try = datetime.utcnow()


@synchronized(lock)
def get(login: str, address: str):
	return attemps.get(login, {}).get(address, Infos(count=0, last_try=datetime(1970)))


@synchronized(lock)
def reset(login: str, address: str):
	if login in attemps and address in login[attemps]:
		del attemps[login][address]


def totime(count: int):
	if count < 3:
		return timedelta(seconds=0)
	elif count < 10:
		return timedelta(seconds=15)
	elif count < 25:
		return timedelta(minutes=1)
	elif count < 50:
		return timedelta(minutes=15)
	else:
		return timedelta(hours=1)

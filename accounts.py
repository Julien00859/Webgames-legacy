import secrets
from datetime import datetime, timedelta
from collections import namedtuple
from typing import Dict

Account = namedtuple("Account", ["tokens", "tries"])
Try = namedtuple("Try", ["count", "lock_until"])
accounts: Dict[int, Account] = {}

token_len: int
token_validity: timedelta

def register(user_id: int) -> str:
    token = secrets.token_urlsafe(token_len)
    expiration = datetime.now() + token_validity

    if user_id not in accounts:
        accounts[user_id] = Account(tokens={}, tries={})

    accounts[user_id].tokens[token] = expiration

    return token

def fail(user_id: int, addr: str) -> datetime:

    now = datetime.now()

    if user_id not in accounts:
        accounts[user_id] = Account(tokens={}, tries={})

    if addr not in account[user_id].tries:
        account[user_id].tries[addr] = Try(count=1, lock_until=now)
        return datetime.now()

    account[user_id].tries[addr].count += 1
    if account[user_id].tries[addr].count < 5:
        account[user_id].tries[addr].lock_until = now
    elif account[user_id].tries[addr].count > 20:
        account[user_id].tries[addr].lock_until = now + timedelta(days=1)
    else:
        time = 2 ** account[user_id].tries[addr].count
        account[user_id].tries[addr].lock_until = now + timedelta(seconds=time)

    return account[user_id].tries[addr].lock_until

def is_lock(user_id: int, addr: str) -> bool:
    return all([addr in accounts[user_id].tries,
                datetime.now() < accounts[user_id].tries[addr].lock_until])

def is_valid(user_id: int, token: str) -> bool:
    if user_id not in accounts or token not in accounts[user_id].tokens:
        return False

    accounts[user_id].tokens[token] = datetime.now() + token_validity
    return True

def remove(user_id: int, token: str):
    del accounts[user_id].tokens[token]

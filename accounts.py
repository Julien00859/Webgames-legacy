# TODO: redis

import secrets
from datetime import datetime, timedelta
from typing import Dict, NamedTuple, NewType

# data structure:
# accounts: {
#     UserName: {
#         tokens: {
#             Token: datetime,
#             ...
#         },
#         tries: {
#             Address: {
#                 count: int,
#                 lock_until: datetime
#             },
#             ...
#         }
#     },
#     ...
# }

Token = NewType("Token", str)
IPAddress = NewType("IPAddress", str)
UserName = NewType("UserName", str)

class Try(NamedTuple):
    count: int
    lock_until: datetime

class Account(NamedTuple):
    tokens: Dict[Token, datetime]
    tries: Dict[IPAddress, Try]

accounts: Dict[UserName, Account] = {}

token_length: int
token_validity: timedelta


def register(user: UserName) -> Token:
    """Register a user and give him a newly generated token"""

    token = secrets.token_urlsafe(token_length)
    expiration = datetime.now() + token_validity

    if user not in accounts:
        accounts[user] = Account(tokens={}, tries={})

    accounts[user].tokens[token] = expiration

    return token


def fail(user: UserName, addr: IPAddress) -> datetime:
    """Increment the fail-count for the given address
       and calculate when the user can retry to connect"""

    now = datetime.now()

    if user not in accounts:
        accounts[user] = Account(tokens={}, tries={})

    if addr not in account[user].tries:
        account[user].tries[addr] = Try(count=1, lock_until=now)
        return datetime.now()

    account[user].tries[addr].count += 1
    if account[user].tries[addr].count < 5:
        account[user].tries[addr].lock_until = now
    elif account[user].tries[addr].count > 20:
        account[user].tries[addr].lock_until = now + timedelta(days=1)
    else:
        time = 2 ** account[user].tries[addr].count
        account[user].tries[addr].lock_until = now + timedelta(seconds=time)

    return account[user].tries[addr].lock_until


def is_locked(user: UserName, addr: IPAddress) -> bool:
    """Check if the user can attemp to connect"""

    return all([user in accounts,
                addr in accounts[user].tries,
                datetime.now() < accounts[user].tries[addr].lock_until])


def is_valid(user: UserName, token: Token) -> bool:
    """Check if the token is valid and still usable"""

    if user not in accounts or token not in accounts[user].tokens:
        return False

    if accounts[user].tokens[token] < datetime.now():
        remove(user, token)
        return False

    accounts[user].tokens[token] = datetime.now() + token_validity
    return True


def remove(user: UserName, token: Token):
    del accounts[user].tokens[token]
    if not accounts[user].tokens:
        del accounts[user]

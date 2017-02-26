from binascii import hexlify
from os import urandom

tokens = {}
length = 0

def add(user_id):
    if user_id in tokens:
        raise KeyError()

    token = hexlify(urandom(length)).decode()
    tokens[user_id] = token
    return token

def remove(user_id):
    if user_id not in tokens:
        raise KeyError()

    del tokens[user_id]

def is_valid(user_id, token):
    return tokens.get(user_id) == token

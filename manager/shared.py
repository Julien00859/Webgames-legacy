"""Shared object to avoid import loop"""

redis = None
http = None
clients = set()
manager_id = None
queues = list()
redis_scripts = {}
udpbroadcaster = None

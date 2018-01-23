"""Shared object to avoid import loop"""
from typing import Dict, List, Tuple

redis = None
http = None
uid_to_client: Dict["UUID", "ClientHandler"] = {}
manager_id = None
queues: List[str] = list()
udpbroadcaster = None
ready_check: Dict["UUID", Tuple[Dict["UUID", bool], "IPAddress"]] = {}
games: Dict["UUID", "Game"] = {}

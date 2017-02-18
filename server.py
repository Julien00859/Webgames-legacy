import asyncio
import uvloop
from haiohttp import web
import socketio

asyncio.set_event_loop_policy(uvloop_EventLoopPolicy())

loop = asyncio.get_event_loop()



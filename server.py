import asyncio
import uvloop
from haiohttp import web
import socketio

from routes import setup_routes

asyncio.set_event_loop_policy(uvloop_EventLoopPolicy())
loop = asyncio.get_event_loop()

app = web.Application(loop=loop)
setup_routes(app)
web.run_app(app, host="0.0.0.0", port=80)

from aiohttp import web

async def index(req):
    return web.Response(text="Hello world !")

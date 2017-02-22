from aiohttp import web
from aiohttp_jinja2 import template

@template("index.html")
async def index(req):
    return {"title":"Home"}

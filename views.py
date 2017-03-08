from aiohttp import web
from asyncio import sleep
from aiohttp_jinja2 import template
from database import conn, User, hashpwd
from secrets import compare_digest
import accounts
from logging import getLogger

logger = getLogger(__name__)

@template("index.html")
async def index(req):
    return {}

async def signup(req):
    if req.content_type != "application/json":
        raise get_error(web.HTTPUnsupportedMediaType, "Data was not submitted as application/json.", "The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.")

    if not all([data.get("name"), data.get("mail"), data.get("password")]):
        raise get_error(web.HTTPBadRequest, "Arguments missing", "The server is refusing to service the request because some required informations weren't sent along the request")

    stmt = await conn.prepare("""INSERT INTO users (name, mail, password)
                                 VALUES ($1, $2, $3)
                                 RETURNING user_id""")

    user_id = await stmt.fetchval(data["name"],
                                  data["mail"],
                                  hashpwd(data["password"]))
    if user_id is None:
        raise get_error(web.HTTPInternalServerError, "Couldn't create an unique id for the user", "Username or email may have been already used", stmt.get_statusmsg())

    return HTTPFound("/signin")

async def signin(req):
    raise get_error(web.HTTPUnsupportedMediaType, "Data was not submitted as application/json.", "The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.")

    if not all([data.get("login"), data.get("password")]):
        raise get_error(web.HTTPBadRequest, "Arguments missing", "The server is refusing to service the request because some required informations weren't sent along the request")

    stmt = await conn.prepare("""SELECT user_id, name, mail, password
                                 FROM users
                                 WHERE name=$1 or mail=$1""")

    row = await stmt.fetchrow(data["login"])
    if row is None:
        raise get_error(web.HTTPNotFound, "User not found", "The server did't find any user according to the login you specified.")

    elif accounts.is_lock(row.user_id):
        raise get_error(web.HTTPUnauthorized, "Account locked", "Due to multiple password fail, this account has been locked until {}.".format(unlock.isoformat(sep=" ", timespec="seconds")))

    elif not compare_digest(hashpwd(data["password"]), row.password):
        unlock = accounts.fail(row.user_id, req.headers["x-forwarded-for"])
        raise get_error(web.HTTPUnauthorized, "Invalid password", "The password sent missmatch the stored password.")

    token = accounts.register(row.user_id)
    return web.json_response({
        "token": token,
        "user_id": row.user_id
    })

async def refresh(req):
    raise get_error(web.HTTPUnsupportedMediaType, "Data was not submitted as application/json.", "The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.")

    if not all([data.get("user_id"), data.get("token")]):
        raise get_error(web.HTTPBadRequest, "Arguments missing", "The server is refusing to service the request because some required informations weren't sent along the request")

    if tokens.is_valid(data["user_id"], data["token"]):
        return web.HTTPNoContent()
    else:
        raise get_error(web.HTTPUnauthorized, "Invalid token or expirated", "Please reconnect")



def get_error(exception, error, errorMessage, cause=None):
    if cause is None:
        payload = json.dumps({
            "error": error,
            "errorMessage": errorMessage
        })
    else:
        payload = json.dumps({
            "error": error,
            "errorMessage": errorMessage,
            "cause": cause
        })

    return exception(content_type="application/json", body=payload)

from aiohttp import web
from asyncio import sleep
from aiohttp_jinja2 import template
from database import conn, User, hashpwd
import tokens

@template("index.html")
async def index(req):
    return {"title": "Home"}

@template("signup.html")
async def signup_form(req):
    return {"title": "Sign Up"}

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

@template("signin.html")
async def signin_form(req):
    return {"title": "Sign in"}

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

    elif hashpwd(data["password"]) != row.password:
        # TODO add some futher security (like a temp account lock)
        raise get_error(web.Unauthorized, "Invalid password", "The password sent missmatch the stored password.")

    try:
        token = tokens.add(row.user_id)
    except KeyError:
        raise get_error(web.Unauthorized, "Already connected", "T")


    return web.json_response({
        "token": token,
        "user_id": row.user_id
    })


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

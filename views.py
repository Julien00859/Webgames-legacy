from sanic.response import json, html, redirect, text
from sanic.exceptions import *
from jinja2 import Template
from os import sep
from secrets import compare_digest
from smtplib import SMTP
from email.message import EmailMessage
from logging import getLogger

import challenges
import accounts
from database import User, Guest

logger = getLogger(__name__)
template = Template(open("client" + sep + "index.html").read())

async def index(req):
    return html(template.render())


async def signup(req):
    if any(map(lambda key: key not in req.json, ["name", "email", "password"])):
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    if not await User.is_free(req.json["name"], req.json["email"]):
        logger.debug(f"Request is {req.json} but name or email is already taken")
        raise InvalidUsage("Username or email already taken")

    guest = Guest(req.json["name"], req.json["email"], User.hashpwd(req.json["password"]))

    chlg = await challenges.create_for(guest)

    logger.info(f"Guest signed up with name: {guest.name} and email: {guest.email}. Challenge generated: {chlg}")
    with open("mails" + sep + "challenge.txt") as mailtext:
        mail = EmailMessage()
        mail.set_content(mailtext.read().format(domain=req.app.config.domain,
                                                scheme="https" if req.app.config.schemessl else "http",
                                                challenge=chlg))
        mail["Subject"] = "WebGames Registration Challenge"
        mail["From"] = req.app.config.smtpuser
        mail["To"] = guest.email

        with SMTP(req.app.config.smtphost, req.app.config.smtpport) as smtp:
            if req.app.config.smtpssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            else:
                smtp.helo()
            smtp.login(req.app.config.smtpuser, req.app.config.smtppwd)
            smtp.send_message(mail)

    return text(f"Challenge sent to {guest.email}")


async def signin(req):
    if any(map(lambda key: key not in req.json, ["login", "password"])):
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    user = await User.get_by_login(req.json["login"])
    if user is None:
        logger.debug(f"Request is {req.json} but user coundn't be found.")
        raise NotFound("User not found")

    if await accounts.is_frozen(user.id, req.ip):
        logger.debug(f"Request is {req.json} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not compare_digest(user.password, User.hashpwd(req.json["password"])):
        logger.debug(f"Request is {req.json} but the password is invalid.")
        unfreeze = await accounts.freeze(user.id, req.ip)
        raise InvalidUsage("Invalid password. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

    await accounts.unfreeze(user.id, req.ip)
    token = await accounts.register(user.id)
    logger.info(f"User {user.name} connected. Token generated: {token}")
    return json({"token": token, "id": user.id, "name": user.name})


async def refresh(req):
    if "id" not in req.json or "token" not in req.json:
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    user = User.get_by_id(req.json["id"])
    if user is None:
        logger.debug(f"Request is {req.json} but user coundn't be found.")
        raise NotFound("User not found")

    if await accounts.is_frozen(user.id, req.ip):
        logger.debug(f"Request is {req.json} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not await accounts.is_valid(req.json["id"], req.json["token"]):
        logger.debug(f"Request is {req.json} but the token is invalid or expirated.")
        await accounts.freeze(user.id, req.ip)
        raise NotFound("Token not found or expirated")

    await accounts.unfreeze(user.id, req.ip)
    logger.info(f"User {user.name} refreshed it's token: {req.json['token']}")
    return json({"token": req.json["token"], "id": user.id, "name": user.name})


async def signout(req):
    if "id" not in req.json or "token" not in req.json:
        raise InvalidUsage("Missing arguments")

    if await accounts.is_valid(req.json["id"], req.json["token"]):
        await accounts.remove(req.json["id"], req.json["token"])


async def challenge(req, token):
    if await challenges.is_frozen(req.ip):
        logger.debug(f"Challenge is {token} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not await challenges.solve(token):
        logger.debug(f"Challenge {token} is invalid.")
        unfreeze = await challenges.freeze(req.ip)
        raise InvalidUsage("Invalid token. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

    await challenges.unfreeze(req.ip)
    logger.info(f"Challenge {token} validated")
    return redirect(req.app.url_for("index"))


async def websock(req, ws):
    while True:
        data = await ws.recv()
        print(data)
        await ws.send(data)

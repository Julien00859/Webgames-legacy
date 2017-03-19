import database as db
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

logger = getLogger(__name__)
template = Template(open("client" + sep + "index.html").read())

async def index(req):
    return html(template.render())


async def signup(req):
    if any(map(lambda key: key not in req.json, ["name", "email", "password"])):
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    if not await db.is_user_free(req.json["name"], req.json["email"]):
        logger.debug(f"Request is {req.json} but name or email is already taken")
        raise InvalidUsage("Username or email already taken")

    user = db.User(req.json["name"], req.json["email"], db.hashpwd(req.json["password"]))

    chlg = challenges.create_for(user)

    logger.info(f"User signed up with name: {user.name} and email: {user.email}. Challenge generated: {chlg}")
    with open("mails" + sep + "challenge.txt") as mailtext:
        mail = EmailMessage()
        mail.set_content(mailtext.read().format(domain=req.app.config.domain,
                                                scheme="https" if req.app.config.schemessl else "http",
                                                challenge=chlg))
        mail["Subject"] = "WebGames Registration Challenge"
        mail["From"] = req.app.config.smtpuser
        mail["To"] = user.email

        with SMTP(req.app.config.smtphost, req.app.config.smtpport) as smtp:
            if req.app.config.smtpssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            else:
                smtp.helo()
            smtp.login(req.app.config.smtpuser, req.app.config.smtppwd)
            smtp.send_message(mail)

    return text("Challenge sent")


async def signin(req):
    if any(map(lambda key: key not in req.json, ["login", "password"])):
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    user = await db.get_user_by_login(req.json["login"])
    if user is None:
        logger.debug(f"Request is {req.json} but user coundn't be found.")
        raise NotFound("User not found")

    if accounts.is_locked(user.name, req.ip):
        logger.debug(f"Request is {req.json} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not compare_digest(user.password, db.hashpwd(req.json["password"])):
        logger.debug(f"Request is {req.json} but the password is invalid.")
        unfreeze = accounts.fail(user.name, req.ip)
        raise InvalidUsage("Invalid password. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

    token = accounts.register(user.name)
    logger.info(f"User {user.name} connected. Token generated: {token}")
    return json({"token": token, "name": user.name})


async def refresh(req):
    if "name" not in req.json or "token" not in req.json:
        logger.debug(f"Request is {req.json} but some arguments are missing.")
        raise InvalidUsage("Missing argument")

    user = db.get_user_by_name(req.json["name"])
    if user is None:
        logger.debug(f"Request is {req.json} but user coundn't be found.")
        raise NotFound("User not found")

    if accounts.is_locked(user.name, req.ip):
        logger.debug(f"Request is {req.json} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not accounts.is_valid(req.json["name"], req.json["token"]):
        logger.debug(f"Request is {req.json} but the token is invalid or expirated.")
        accounts.fail(user.name, req.ip)
        raise NotFound("Token not found or expirated")

    logger.info(f"User {user.name} refreshed it's token: {req.json['token']}")
    return json({"token": req.json["token"], "name": user.name})


async def signout(req):
    if "name" not in req.json or "token" not in req.json:
        raise InvalidUsage("Missing arguments")

    if accounts.is_valid(req.json["name"], req.json["token"]):
        accounts.remove(req.json["name"], req.json["token"])


async def challenge(req, token):
    if challenges.is_locked(req.ip):
        logger.debug(f"Challenge is {token} but the account is frozen.")
        raise InvalidUsage("Account frozen")

    if not await challenges.solve(token):
        logger.debug(f"Challenge {token} is invalid.")
        unfreeze = challenges.fail(req.ip)
        raise InvalidUsage("Invalid token. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

    logger.info(f"Challenge {token} validated")
    return redirect(req.app.url_for("index"))

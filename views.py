import database as db
from sanic.response import json, html, redirect, text
from sanic.exceptions import *
from jinja2 import Template
from os import sep
from secrets import compare_digest

import challenges
import accounts

template = Template(open("client" + sep + "index.html").read())

async def index(req):
	return html(template.render(name=req.args.get("name", "stranger")))


async def signup(req):
	if any(map(lambda key: key not in req.json, ["name", "email", "password"])):
		raise InvalidUsage("Missing argument")
	
	if not await db.is_user_free(req.json["name"], req.json["email"]):
		raise InvalidUsage("Username or email already taken")

	user = db.User(req.json["name"], req.json["email"], db.hashpwd(req.json["password"]))

	chlg = challenges.create_for(user)

	# send email
	print(chlg)

	return text(chlg)


async def signin(req):
	if any(map(lambda key: key not in req.json, ["login", "password"])):
		raise InvalidUsage("Missing argument")

	user = db.get_user_by_login(req.json["login"])
	if user is None:
		raise NotFound("User not found")

	if accounts.is_locked(user.name, req.ip):
		raise InvalidUsage("Account frozen")

	if not compare_digest(user.password, db.hashpwd(req.json["password"])):
		unfreeze = accounts.fail(user.name, req.ip)
		raise InvalidUsage("Invalid token. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

	token = accounts.register(user.name)

	return json({"token": token, "name": user.name})

	
async def refresh(req):
	if "name" not in req.json or "token" not in req.json:
		raise InvalidUsage("Missing argument")

	user = db.get_user_by_name(req.json["name"])
	if user is None:
		raise NotFound("User not found")

	if accounts.is_locked(user.name, req.ip):
		raise InvalidUsage("Account frozen")

	if not accounts.is_valid(req.json["name"], req.json["token"]):
		accounts.fail(user.name, req.ip)
		raise NotFound("Token not found or expirated")
	
	return json({"token": token, "name": user.name})


async def signout(req):
	if "name" not in req.json or "token" not in req.json:
		raise InvalidUsage("Missing arguments")

	if accounts.is_valid(req.json["name"], req.json["token"]):
		accounts.remove(req.json["name"], req.json["token"])


async def challenge(req, token):
	if challenges.is_locked(req.ip):
		raise InvalidUsage("Account frozen")

	if not await challenges.solve(token):
		unfreeze = challenges.fail(req.ip)
		raise InvalidUsage("Invalid token. Account frozen until " + unfreeze.isoformat(sep=" ", timespec="seconds"))

	return redirect(req.app.url_for("index"))

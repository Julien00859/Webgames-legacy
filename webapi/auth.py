from sanic import Blueprint
from middlewares import authenticate, jsonfields, ClientType, safe_http_exception
from sanic.response import json, text
from sanic.exceptions import Forbidden, InvalidUsage
import jwt as jwtlib
import shared
import bcrypt
from logging import getLogger
from config import JWT_EXPIRATION_TIME, JWT_SECRET, TOKEN_EXPIRATION_TIME
from uuid import uuid4
from secrets import token_urlsafe, compare_digest
from datetime import datetime

logger = getLogger(__name__)
auth_bp = Blueprint("auth", url_prefix="auth")

@auth_bp.route("/session", methods=["POST"])
@safe_http_exception
@jsonfields({"login", "password"})
async def login(req):
    stmt = await shared.postgres.prepare("SELECT userid, password, is_verified, is_admin FROM get_user_by_login($1);")
    user = await stmt.fetchrow(req.json["login"])
    if all(map(lambda v: v is None, user.values())):
        logger.warning(f'User \'{req.json["login"]}\' not found')
        raise Forbidden("User not found")

    if not user["is_verified"]:
        logger.warning(f'User \'{req.json["login"]}\' is not verified yet')
        raise Forbidden("You must verify your email first")

    if not bcrypt.checkpw(req.json["password"].encode(), user["password"]):
        logger.log(45, f'Password for User \'{req.json["login"]}\' does not match (IP: {req.ip})')
        raise Forbidden("Incorrect password")

    jwt = jwtlib.encode({
        "iss": ClientType.WEBAPI.value,
        "sub": "webgames",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + JWT_EXPIRATION_TIME,
        "tid": str(uuid4()),
        "type": ClientType.ADMIN.value if user["is_admin"] else ClientType.USER.value,
        "id": str(user["userid"])
    }, JWT_SECRET)
    logger.info(f"Generated token: {jwt}")
    return json({"token": jwt})

@auth_bp.route("/session", methods=["DELETE"])
@safe_http_exception
@authenticate({ClientType.USER, ClientType.ADMIN})
async def logout(req, jwt):
    await shared.redis.sadd("removed-jwt", jwt["tid"])
    return text("ok")

@auth_bp.route("/account", methods=["GET"])
@safe_http_exception
@authenticate({ClientType.USER, ClientType.ADMIN})
async def get_my_account(req, jwt):
    stmt = await shared.postgres.prepare("SELECT userid, nickname, email, is_verified, is_admin FROM get_user_by_id($1);")
    user = await stmt.fetchrow(jwt["id"])

    return json({
        "userid": str(user["userid"]),
        "nickname": user["nickname"],
        "email": user["email"],
        "is_verified": user["is_verified"],
        "is_admin": user["is_admin"]
    })

@auth_bp.route("/account", methods=["POST"])
@safe_http_exception
@jsonfields({"nickname", "email", "password"})
async def register(req):
    stmt = await shared.postgres.prepare("SELECT create_user($1, $2, $3, $4);")
    userid = uuid4()
    await stmt.fetch(userid,
                     req.json["nickname"], 
                     req.json["email"],
                     bcrypt.hashpw(req.json["password"].encode(), bcrypt.gensalt()))
    validation_token = token_urlsafe()
    await shared.redis.set(f"users:{userid}:validation_token", validation_token)
    await shared.redis.expire(f"users:{userid}:validation_token", TOKEN_EXPIRATION_TIME)

    # TODO
    # send an email

    return json({"id": str(userid), "token": validation_token})
    

@auth_bp.route("/account/forget", methods=["POST"])
@safe_http_exception
@jsonfields({"login"})
async def forget(req):
    stmt = await shared.postgres.prepare("SELECT userid, email, is_verified FROM get_user_by_login($1)")
    user = stmt.fetchrow(req.json["login"])
    if all(map(lambda v: v is None, user.values())):
        logger.warning(f"User \'{req.json['login']}\' not found")
        raise Forbidden("User not found")

    if not user["is_verified"]:
        logger.warning(f'User \'{req.json["login"]}\' is not verified yet')
        raise Forbidden("You must verify your email first")

    reset_token = token_urlsafe()
    await shared.redis.set(f"users:{userid}:reset_token", reset_token)
    await shared.redis.expire(f"users:{userid}:reset_token", TOKEN_EXPIRATION_TIME)

    # TODO
    # send an email

    return json({"token": reset_token})

@auth_bp.route("/account", methods=["PUT"])
@safe_http_exception
@jsonfields({})
@authenticate({ClientType.USER, ClientType.ADMIN})
async def update_my_account(req, jwt):
    allowed_fields = {"nickname", "email", "password"}
    fields = allowed_fields & req.json.keys()
    if not fields:
        logging.warning(f"Unknown fields: {req.json.keys()}")
        raise InvalidUsage(f"Autorized fields are {allowed_fields}")

    async with shared.postgres.transaction():
        sets = " ".join([f"SET {field} = ${idx+2}" for idx, field in enumerate(fields)])
        stmt = await shared.postgres.prepare(f"UPDATE FROM tb_users {sets} WHERE userid = $1")
        await stmt.fetch(jwt["id"], *map(lambda field: req.json[field], fields))
    
    return text("ok")

@auth_bp.route("/account", methods=["DELETE"])
@safe_http_exception
@jsonfields({})
@authenticate({ClientType.USER, ClientType.ADMIN})
async def delete_my_account(req, jwt):
    async with shared.postgres.transaction():
        stmt = await shared.postgres.prepare("DELETE FROM tb_users WHERE userid = $1")
        stmt.fetchv(jwt["id"])

    await shared.redis.sadd("removed-id", jwt["id"])

    return text("ok")

uuid_re = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
@auth_bp.route(f"/accounts/<clientid:{uuid_re}>", methods=["GET"])
@safe_http_exception
@authenticate({ClientType.USER, ClientType.ADMIN})
async def get_account(req, clientid, jwt):
    stmt = await shared.postgres.prepare("SELECT userid, email, is_verified, is_admin FROM get_user_by_id($1);")
    user = await stmt.fetchrow(clientid)

    return json({field: value for field, value in user.items()})

@auth_bp.route(f"/accounts/<clientid:{uuid_re}>/validate/<token>", methods=["GET"])
@safe_http_exception
async def validate(req, clientid, token):
    if not (await shared.redis.exists(f"users:{clientid}:validation_token")):
        logger.log(45, f"No validation token available for user {clientid} (IP: {req.ip})")
        raise Forbidden("No validation token available for this account")

    validation_token = await (shared.redis.get(f"users:{clientid}:validation_token"))
    if not compare_digest(token.encode(), validation_token):
        logger.log(45, f"Wrong validation token for user {clientid} (IP: {req.ip})")
        raise Forbidden("Wrong validation token")

    async with shared.postgres.transaction():
        stmt = await shared.postgres.prepare("SELECT set_user_verified($1);")
        await stmt.fetch(clientid)
    
    return text("ok")

@auth_bp.route(f"/accounts/<clientid:{uuid_re}>/reset/<token>", methods=["POST"])
@safe_http_exception
@jsonfields({"password"})
async def reset(req, clientid, token, id):
    if not (await shared.redis.exists(f"users:{clientid}:reset_token")):
        logger.log(45, f"No reset token available for user {clientid} (IP: {req.ip})")
        raise Forbidden("No reset token available for this account")

    reset_token = await (shared.redis.get(f"users:{clientid}:resettoken"))
    if not compare_digest(token, reset_token):
        logger.log(45, f"Wrong reset token for user {clientid} (IP: {req.ip})")
        raise Forbidden("Wrong reset token")

    async with shared.postgres.transaction():
        stmt = await shared.postgres.prepare("UPDATE FROM tb_users SET password = $1 WHERE userid = $2")
        await stmt.fetch(req.json["password"], clientid)
    
    return text("ok")

@auth_bp.route(f"/accounts/<clientid:{uuid_re}>", methods=["PUT"])
@safe_http_exception
@jsonfields({})
@authenticate({ClientType.ADMIN})
async def update_account(req, clientid, token, jwt):
    allowed_fields = {"nickname", "email", "password", "is_verfied", "is_admin"}
    fields = allowed_fields & req.json.keys()
    if not fields:
        logging.warning(f"Unknown fields: {req.json.keys()}")
        raise InvalidUsage(f"Autorized fields are {allowed_fields}")

    async with shared.postgres.transaction():
        sets = " ".join([f"SET {field} = ${idx+2}" for idx, field in enumerate(fields)])
        stmt = await shared.postgres.prepare(f"UPDATE FROM tb_users {sets} WHERE userid = $1")
        await stmt.fetch(clientid, *map(lambda field: req.json[field], fields))
    
    return text("ok")

@auth_bp.route(f"/accounts/<clientid:{uuid_re}>", methods=["DELETE"])
@safe_http_exception
@jsonfields({})
@authenticate({ClientType.ADMIN})
async def delete_account(req, clientid, token, jwt):
    async with shared.postgres.transaction():
        stmt = await shared.postgres.prepare("DELETE FROM tb_users WHERE userid = $1")
        stmt.fetchv(clientid)

    await shared.redis.sadd("removed-id", clientid)

    return text("ok")
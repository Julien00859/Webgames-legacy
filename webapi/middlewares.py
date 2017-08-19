from sanic.exceptions import Unauthorized, Forbidden, InvalidUsage, SanicException
import jwt as jwtlib
from functools import wraps
from logging import getLogger
from collections import namedtuple
from enum import Enum
from sanic.response import json
from config import JWT_SECRET
import shared

logger = getLogger(__name__)

class ClientType(Enum):
    ADMIN = "admin"
    USER = "user"
    GAME = "game"
    WEBAPI = "webapi"
    MANAGER = "manager"

def safe_http_exception(func):
    @wraps(func)
    async def wrapped(req, *args, **kwargs):
        try:
            return await func(req, *args, **kwargs)
        except SanicException as http_error:
            return json({"error": str(http_error)}, http_error.status_code)
    return wrapped

def authenticate(allowed_types: set):
    def authenticate_wrapper(func):
        @wraps(func)
        async def authenticate_wrapped(req, *args, **kwargs):
            bearer = req.headers.get("Authorization")
            if not bearer:
                logger.warning(f"Authorization header missing (IP: {req.ip})")
                raise Unauthorized("Authorization header required", "Bearer")

            if not bearer.startswith("Bearer:"):
                logger.warning(f"Wrong authorization header type (IP: {req.ip})")
                raise Unauthorized("Bearer authorization type required", "Bearer")

            try:
                jwt = jwtlib.decode(bearer[7:].strip(), JWT_SECRET)
            except jwtlib.exceptions.InvalidTokenError as err:
                logger.log(45, f"Invalid token (IP: {req.ip})")
                raise Forbidden("Invalid token")

            if (await shared.redis.sismember("removed-jwt", jwt["tid"])):
                logger.log(45, f"Token has been removed (IP: {req.ip})")
                raise Forbidden("Invalid token")

            if (await shared.redis.sismember("removed-id", jwt["id"])):
                logger.log(45, f"ID has been removed (IP: {req.ip})")
                raise Forbidden("Invalid ID")
            
            if ClientType(jwt["type"]) not in allowed_types:
                logger.log(45, f"Invalid token type: \"{jwt['type']}\" not in {allowed_types} (IP: {req.ip})")
                raise Forbidden("Invalid token type")

            return await func(req, *args, **kwargs, jwt=jwt)
        return authenticate_wrapped
    return authenticate_wrapper

def jsonfields(fields: set):
    def jsonfields_wrapper(func):
        @wraps(func)
        async def jsonfields_wrapped(req, *args, **kwargs):
            ct = req.headers.get("Content-Type")
            if ct is None or ct != "application/json":
                raise InvalidUsage("JSON required")
            if not fields:
                pass
            if not isinstance(req.json, dict):
                raise InvalidUsage("JSON object required")
            if not req.json:
                raise InvalidUsage(f"Fields {fields} are missing")
            missings = fields - req.json.keys()
            if missings:
                raise InvalidUsage(f"Fields {missings} are missing")
            return await func(req, *args, **kwargs)
        return jsonfields_wrapped
    return jsonfields_wrapper

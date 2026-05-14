from functools import wraps
from flask import request, g
import jwt as pyjwt
from utils.jwt_utils import decode_token
from utils.errors import ApiError


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ApiError("Missing bearer token", 401)
        token = header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except pyjwt.ExpiredSignatureError:
            raise ApiError("Token expired", 401)
        except pyjwt.InvalidTokenError:
            raise ApiError("Invalid token", 401)
        g.user_id = payload["sub"]
        g.user_email = payload.get("email")
        return fn(*args, **kwargs)
    return wrapper

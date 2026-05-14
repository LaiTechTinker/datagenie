import re
import bcrypt
from models import user as user_model
from utils.errors import ApiError
from utils.jwt_utils import encode_token

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate(email: str, password: str):
    if not email or not EMAIL_RE.match(email):
        raise ApiError("Invalid email", 400)
    if not password or len(password) < 6:
        raise ApiError("Password must be at least 6 characters", 400)


def signup(email: str, password: str) -> dict:
    _validate(email, password)
    if user_model.find_by_email(email):
        raise ApiError("Email already registered", 409)
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = user_model.create(email, pw_hash)
    token = encode_token(str(user["_id"]), user["email"])
    return {"token": token, "user": user_model.serialize(user)}


def login(email: str, password: str) -> dict:
    _validate(email, password)
    user = user_model.find_by_email(email)
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise ApiError("Invalid credentials", 401)
    token = encode_token(str(user["_id"]), user["email"])
    return {"token": token, "user": user_model.serialize(user)}

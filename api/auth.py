from flask import Blueprint, request, jsonify, g
from services import auth_service
from models import user as user_model
from utils.decorators import auth_required
from utils.errors import ApiError

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    body = request.get_json() or {}
    return jsonify(auth_service.signup(body.get("email", ""), body.get("password", ""))), 201


@auth_bp.post("/login")
def login():
    body = request.get_json() or {}
    return jsonify(auth_service.login(body.get("email", ""), body.get("password", "")))


@auth_bp.get("/me")
@auth_required
def me():
    user = user_model.find_by_id(g.user_id)
    if not user:
        raise ApiError("User not found", 404)
    return jsonify(user=user_model.serialize(user))

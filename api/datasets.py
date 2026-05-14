from flask import Blueprint, request, jsonify, g
from services import dataset_service
from utils.decorators import auth_required

datasets_bp = Blueprint("datasets", __name__)


@datasets_bp.get("")
@auth_required
def list_datasets():
    return jsonify(datasets=dataset_service.list_user(g.user_id))


@datasets_bp.post("/upload")
@auth_required
def upload():
    f = request.files.get("file")
    return jsonify(dataset=dataset_service.upload(g.user_id, f)), 201


@datasets_bp.get("/<dataset_id>")
@auth_required
def get_one(dataset_id):
    return jsonify(dataset=dataset_service.get(g.user_id, dataset_id))


@datasets_bp.delete("/<dataset_id>")
@auth_required
def delete_one(dataset_id):
    dataset_service.delete(g.user_id, dataset_id)
    return jsonify(ok=True)

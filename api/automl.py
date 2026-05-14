from flask import Blueprint, request, jsonify, g
from services import automl_service
from utils.decorators import auth_required

automl_bp = Blueprint("automl", __name__)


@automl_bp.post("/jobs")
@auth_required
def start():
    body = request.get_json() or {}
    job = automl_service.start(
        user_id=g.user_id,
        dataset_id=body.get("datasetId"),
        target=body.get("target"),
        problem_type=body.get("problemType", "classification"),
        test_size=float(body.get("testSize", 0.2)),
        random_state=int(body.get("randomState", 42)),
    )
    return jsonify(job=job), 201


@automl_bp.get("/jobs")
@auth_required
def list_jobs():
    return jsonify(jobs=automl_service.list_user(g.user_id))


@automl_bp.get("/jobs/<job_id>")
@auth_required
def get(job_id):
    return jsonify(job=automl_service.get(job_id))

from flask import Blueprint, jsonify, g
from services import viz_service
from utils.decorators import auth_required

viz_bp = Blueprint("visualizations", __name__)


@viz_bp.post("/<dataset_id>/visualizations")
@auth_required
def suggest(dataset_id):
    return jsonify(viz_service.suggestions(g.user_id, dataset_id))

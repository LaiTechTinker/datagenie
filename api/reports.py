import io

from flask import Blueprint, request, jsonify, g, send_file
from services import report_service
from utils.decorators import auth_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.post("")
@auth_required
def generate():
    body = request.get_json() or {}
    dataset_id = body.get("datasetId")
    if not dataset_id:
        return jsonify(error="datasetId required"), 400
    return jsonify(report=report_service.generate_for_dataset(g.user_id, dataset_id)), 201


@reports_bp.get("/<report_id>")
@auth_required
def get(report_id):
    return jsonify(report=report_service.get(report_id))

# @reports_bp.get("/<report_id>/pdf")
# @auth_required
# def get_pdf(report_id):
#     pdf_path=report_service.send_pdf_file(report_id)
#     return send_file(pdf_path, mimetype='application/pdf', as_attachment=False)

@reports_bp.get("/<report_id>/pdf")
@auth_required
def get_pdf(report_id):
    pdf_bytes, filename = report_service.get_pdf_for_report(g.user_id, report_id)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@reports_bp.post("/<report_id>/chat")
@auth_required
def chat(report_id):
    body = request.get_json() or {}
    return jsonify(report_service.chat(report_id, body.get("message", "")))


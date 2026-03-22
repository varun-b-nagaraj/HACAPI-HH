from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
report_bp = Blueprint("report", __name__, url_prefix="/api")


@report_bp.route("/getReport", methods=["POST"])
def get_report():
    payload, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    student_id = str(payload.get("student_id", "")).strip()

    try:
        if student_id and not session.switch_student(student_id):
            return jsonify({"error": f"Failed to switch to student {student_id}"}), 400

        report_data = session.get_report()
        if not report_data:
            return jsonify({"error": "Failed to retrieve report"}), 404

        return jsonify(report_data), 200
    except Exception as exc:
        logger.exception("Error in /getReport")
        return jsonify({"error": str(exc)}), 500


@report_bp.route("/getIpr", methods=["POST"])
def get_ipr():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        ipr_data = session.get_report()
        if ipr_data is None:
            return jsonify({"error": "Failed to retrieve progress report"}), 404
        return jsonify(ipr_data), 200
    except Exception as exc:
        logger.exception("Error in /getIpr")
        return jsonify({"error": str(exc)}), 500

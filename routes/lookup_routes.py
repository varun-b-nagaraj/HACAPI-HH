from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
lookup_bp = Blueprint("lookup", __name__, url_prefix="/lookup")


@lookup_bp.route("/students", methods=["POST"])
def get_student_list():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        students = session.get_students()
        if not students:
            logger.info("No students found for user: %s", session.username)
            return jsonify({"error": "No students found"}), 404
        return jsonify({"students": students}), 200
    except Exception as exc:
        logger.exception("Error in /lookup/students for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500


@lookup_bp.route("/switch", methods=["POST"])
def switch_student():
    payload, session, err_json, err_code = build_hac_session_from_request(require_student_id=True)
    if err_json:
        return err_json, err_code

    student_id = str(payload.get("student_id", "")).strip()

    try:
        success = session.switch_student(student_id)
        if success:
            logger.info("Switched to student_id: %s for user: %s", student_id, session.username)
            return jsonify({"success": True, "message": f"Switched to student {student_id}"}), 200

        logger.warning("Failed switch to student_id: %s for user: %s", student_id, session.username)
        return jsonify({"success": False, "error": f"Failed to switch to student ID {student_id}"}), 400
    except Exception as exc:
        logger.exception("Error in /lookup/switch for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500


@lookup_bp.route("/current", methods=["POST"])
def get_current_student():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        active_student = session.get_active_student()
        if not active_student:
            logger.info("No active student found for user: %s", session.username)
            return jsonify({"success": False, "error": "No active student found"}), 404
        return jsonify({"success": True, "active_student": active_student}), 200
    except Exception as exc:
        logger.exception("Error in /lookup/current for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
assignments_bp = Blueprint("assignments", __name__, url_prefix="/api")


@assignments_bp.route("/getAssignments", methods=["POST"])
def get_assignments():
    payload, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    class_name = str(payload.get("class") or "").strip()

    try:
        assignments = session.fetch_class_assignments(class_name if class_name else None)
        if assignments is None:
            logger.warning("No assignments found for user: %s", session.username)
            return jsonify({"error": "No assignments found or failed to retrieve"}), 404
        return jsonify(assignments), 200
    except Exception as exc:
        logger.exception("Exception in /getAssignments for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
grades_bp = Blueprint("grades", __name__, url_prefix="/api")


@grades_bp.route("/getAverages", methods=["POST"])
def get_averages():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        averages_data = session.get_averages()
        if averages_data is None:
            logger.warning("Failed to retrieve averages for user: %s", session.username)
            return jsonify({"error": "Failed to retrieve averages"}), 404
        return jsonify(averages_data), 200
    except Exception as exc:
        logger.exception("Exception during /getAverages for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
info_bp = Blueprint("info", __name__, url_prefix="/api")


@info_bp.route("/getInfo", methods=["POST"])
def get_info():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        info_data = session.get_info()
        if info_data is None:
            logger.warning("No info found for user: %s", session.username)
            return jsonify({"error": "Failed to retrieve information"}), 404
        return jsonify(info_data), 200
    except Exception as exc:
        logger.exception("Exception in /getInfo for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/getName", methods=["POST"])
def get_name():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        name = session.get_name()
        if name:
            logger.info("Successfully fetched name for user: %s", session.username)
            return jsonify({"name": name}), 200
        logger.warning("No name returned for user: %s", session.username)
        return jsonify({"error": "Unable to fetch name"}), 404
    except Exception as exc:
        logger.exception("Exception in /getName for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

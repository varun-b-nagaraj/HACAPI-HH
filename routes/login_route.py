from flask import Blueprint, request, jsonify
from hac.session import HACSession
from extensions import limiter
import logging

login_bp = Blueprint("login", __name__)
logger = logging.getLogger(__name__)


@login_bp.route("/api/login", methods=["POST"], strict_slashes=False)
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    base_url = str(data.get("base_url") or "https://accesscenter.roundrockisd.org/").strip()

    if not username or not password:
        logger.warning("Login attempt with missing username or password")
        return jsonify({"error": "Missing username or password"}), 400

    try:
        session = HACSession(username, password, base_url)
        session.login()
    except PermissionError:
        logger.warning("Invalid credentials for user: %s", username)
        return jsonify({"error": "Invalid credentials or HAC login failed"}), 401
    except ValueError as ve:
        logger.warning("ValueError during login for user %s: %s", username, ve)
        return jsonify({"error": str(ve)}), 400
    except Exception as exc:
        logger.exception("Unexpected error during login for user %s", username)
        return jsonify({"error": f"Unexpected login failure: {str(exc)}"}), 500

    logger.info("Successful login validation for user: %s", username)
    return jsonify({"success": True}), 200

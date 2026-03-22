from flask import Blueprint, jsonify
import logging
from .hac_auth import build_hac_session_from_request

logger = logging.getLogger(__name__)
transcript_bp = Blueprint("transcript", __name__, url_prefix="/api")


@transcript_bp.route("/getTranscript", methods=["POST"])
def get_transcript():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        data = session.get_transcript()
        if not data:
            logger.warning("Transcript data not found for user: %s", session.username)
            return jsonify({"error": "Transcript not available"}), 404
        return jsonify(data), 200
    except Exception as exc:
        logger.exception("Exception in /getTranscript for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500


@transcript_bp.route("/getRank", methods=["POST"])
def get_rank():
    _, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    try:
        rank = session.get_rank()
        if rank is None and rank != 0:
            logger.warning("Rank data not found for user: %s", session.username)
            return jsonify({"error": "Rank not available"}), 404
        return jsonify({"rank": rank}), 200
    except Exception as exc:
        logger.exception("Exception in /getRank for user: %s", session.username)
        return jsonify({"error": str(exc)}), 500

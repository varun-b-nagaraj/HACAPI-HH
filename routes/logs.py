from flask import Blueprint, jsonify
from supabase import create_client
import os
import logging
from .hac_auth import build_hac_session_from_request

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")
logger = logging.getLogger(__name__)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)


@logs_bp.route("/checkout", methods=["POST"])
def log_checkout():
    payload, _, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    required_fields = ["student_id", "student_name", "class_name", "period", "room", "teacher", "checkout_time"]
    if not all(field in payload for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    record = {
        "student_id": str(payload["student_id"]),
        "student_name": payload["student_name"],
        "class_name": payload["class_name"],
        "period": int(payload["period"]),
        "room": payload["room"],
        "teacher": payload["teacher"],
        "checkout_time": payload["checkout_time"]
    }

    try:
        res = supabase.table("checkouts").insert(record).execute()
        if res.data:
            return jsonify(res.data[0]), 201
        return jsonify({"error": "Insert failed"}), 500
    except Exception as exc:
        logger.exception("Exception during Supabase checkout insert")
        return jsonify({"error": str(exc)}), 500


@logs_bp.route("/checkin", methods=["POST"])
def log_checkin():
    payload, _, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    if not all(k in payload for k in ("checkout_id", "checkin_time", "duration_sec")):
        return jsonify({"error": "Missing checkout_id, checkin_time, or duration_sec"}), 400

    try:
        res = (
            supabase.table("checkouts")
            .update({
                "checkin_time": payload["checkin_time"],
                "duration_sec": int(payload["duration_sec"])
            })
            .eq("id", payload["checkout_id"])
            .execute()
        )

        if res.data:
            return jsonify(res.data), 200
        return jsonify({"error": "Update failed"}), 404
    except Exception as exc:
        logger.exception("Exception during Supabase checkin update")
        return jsonify({"error": str(exc)}), 500

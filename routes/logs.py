from flask import Blueprint, jsonify
import os
import logging
from .hac_auth import build_hac_session_from_request

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")
logger = logging.getLogger(__name__)

_supabase_client = None
_supabase_init_error = None


def get_supabase_client():
    global _supabase_client, _supabase_init_error

    if _supabase_client is not None:
        return _supabase_client, None

    if _supabase_init_error is not None:
        return None, _supabase_init_error

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        _supabase_init_error = "Supabase credentials are not configured."
        logger.warning(_supabase_init_error)
        return None, _supabase_init_error

    try:
        from supabase import create_client
        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client, None
    except Exception as exc:
        _supabase_init_error = str(exc)
        logger.exception("Failed to initialize Supabase client")
        return None, _supabase_init_error


@logs_bp.route("/checkout", methods=["POST"])
def log_checkout():
    payload, _, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    supabase, supabase_err = get_supabase_client()
    if supabase is None:
        return jsonify({"error": supabase_err}), 503

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

    supabase, supabase_err = get_supabase_client()
    if supabase is None:
        return jsonify({"error": supabase_err}), 503

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

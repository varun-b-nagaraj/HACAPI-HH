from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify
from .hac_auth import build_hac_session_from_request

daytype_bp = Blueprint("daytype", __name__, url_prefix="/api")


def _parse_target_date(payload):
    raw = str(payload.get("target_date") or payload.get("date") or "").strip()
    if not raw:
        return datetime.now(ZoneInfo("America/Chicago")).date(), None

    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date(), None
        except ValueError:
            continue

    return None, (
        jsonify({"error": "Invalid date format. Use YYYY-MM-DD or MM/DD/YYYY"}),
        400,
    )


@daytype_bp.route("/getDayType", methods=["POST"])
def get_day_type():
    payload, session, err_json, err_code = build_hac_session_from_request()
    if err_json:
        return err_json, err_code

    target_date, parse_error = _parse_target_date(payload)
    if parse_error:
        return parse_error

    result = session.get_week_day_type(target_date)
    if result is None:
        return jsonify({"error": "Unable to parse WeekView day type"}), 404

    if not result.get("day_type"):
        result["message"] = "No day type found for this date. This is likely a weekend or non-school day."

    return jsonify(result), 200

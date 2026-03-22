from flask import request, jsonify
from hac.session import HACSession

DEFAULT_HAC_BASE_URL = "https://accesscenter.roundrockisd.org/"


def _read_payload():
    return request.get_json(silent=True) or {}


def get_credentials_from_request(require_student_id=False):
    payload = _read_payload()

    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    base_url = str(payload.get("base_url") or DEFAULT_HAC_BASE_URL).strip()

    if not username or not password:
        return None, None, jsonify({"error": "Missing username or password"}), 400

    if require_student_id:
        student_id = str(payload.get("student_id", "")).strip()
        if not student_id:
            return None, None, jsonify({"error": "Missing student_id"}), 400

    return payload, {"username": username, "password": password, "base_url": base_url}, None, None


def build_hac_session_from_request(require_student_id=False):
    payload, creds, err_json, err_code = get_credentials_from_request(require_student_id=require_student_id)
    if err_json:
        return None, None, err_json, err_code

    try:
        session = HACSession(creds["username"], creds["password"], creds["base_url"])
        session.login()
        return payload, session, None, None
    except PermissionError:
        return None, None, jsonify({"error": "Invalid credentials or HAC login failed"}), 401
    except ValueError as ve:
        return None, None, jsonify({"error": str(ve)}), 400
    except Exception as exc:
        return None, None, jsonify({"error": str(exc)}), 500

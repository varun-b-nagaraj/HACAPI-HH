from flask import Blueprint, jsonify

logout_bp = Blueprint("logout", __name__, url_prefix="/api")


@logout_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"success": True, "message": "Logged out locally"}), 200

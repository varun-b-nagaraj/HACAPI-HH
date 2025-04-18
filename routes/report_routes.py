from flask import Blueprint, request, jsonify
from hac.session import HACSession

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/getReport", methods=["GET"])
def get_report():
    user = request.args.get('user')
    password = request.args.get('pass')
    link = request.args.get('link', 'https://accesscenter.roundrockisd.org/')
    student_id = request.args.get('student_id')
    
    session = HACSession(user, password, link)
    
    if student_id:
        success = session.switch_student(student_id)
        if not success:
            return jsonify({"error": f"Failed to switch to student ID {student_id}"}), 400
    
    data = session.get_report()
    return jsonify(data)

@report_bp.route("/api/getIpr", methods=["GET"])
def get_ipr():
    user = request.args.get('user')
    password = request.args.get('pass')
    link = request.args.get('link', 'https://accesscenter.roundrockisd.org/')

    session = HACSession(user, password, link)
    data = session.get_progress_report()
    return jsonify(data)

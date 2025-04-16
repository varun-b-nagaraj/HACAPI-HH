# routes/__init__.py

from .info_routes        import info_bp
from .grades_routes      import grades_bp
from .assignments_routes import assignments_bp
from .auth_routes        import auth_bp
from .transcript_routes  import transcript_bp
from .report_routes      import report_bp
from .lookup_routes      import lookup_bp
from .logs               import logs_bp  

def register_routes(app):
    app.register_blueprint(info_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(transcript_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(lookup_bp)
    app.register_blueprint(logs_bp)

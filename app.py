from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from routes import register_routes
from dotenv import load_dotenv
from extensions import limiter
import os

load_dotenv()
ALLOWED_CORS_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS"


def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers="*",
        expose_headers="*",
        supports_credentials=False,
        max_age=86400,
    )
    app.config["RATELIMIT_DEFAULT"] = "100 per hour"
    limiter.init_app(app)

    register_routes(app)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return ("", 204)

    @app.after_request
    def add_cors_headers(response):
        request_headers = request.headers.get("Access-Control-Request-Headers")
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = ALLOWED_CORS_METHODS
        response.headers["Access-Control-Allow-Headers"] = request_headers if request_headers else "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    if os.getenv("FLASK_ENV") != "development":
        @app.before_request
        def enforce_https():
            if not request.is_secure:
                return redirect(request.url.replace("http://", "https://"), code=301)

    @app.route("/")
    def home():
        return jsonify({"success": True, "message": "Welcome to the HAC API."})

    @app.errorhandler(429)
    def ratelimit_handler(_):
        return jsonify({"error": "Rate limit exceeded"}), 429

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)

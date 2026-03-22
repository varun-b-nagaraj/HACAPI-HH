from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from routes import register_routes
from dotenv import load_dotenv
from extensions import limiter
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    CORS(app)
    app.config["RATELIMIT_DEFAULT"] = "100 per hour"
    limiter.init_app(app)

    register_routes(app)

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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

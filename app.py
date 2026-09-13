import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, request

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = (ROOT_DIR / "backend").resolve()
MAIN_PAGE_DIR = (ROOT_DIR / "main-page").resolve()
FRONTEND_OUT_DIR = (ROOT_DIR / "frontend" / "out").resolve()

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import Config
from utils.logger import logger
from middleware.security import init_security
from middleware.rate_limit import init_rate_limiter
from blueprints.health import health_bp
from blueprints.chat import chat_bp
from blueprints.suggestions import suggestions_bp
from blueprints.members import members_bp
from blueprints.events_bp import events_bp


def create_app() -> Flask:
    app = Flask(
        "drax",
        root_path=str(ROOT_DIR),
        instance_path=str(ROOT_DIR / "instance"),
        static_folder=None,
    )
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    init_security(app)
    init_rate_limiter(app)

    # Register blueprints under /api/v1
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(chat_bp, url_prefix="/api/v1")
    app.register_blueprint(suggestions_bp, url_prefix="/api/v1")
    app.register_blueprint(members_bp, url_prefix="/api/v1")
    app.register_blueprint(events_bp, url_prefix="/api/v1")

    # Register aliases under /api
    app.register_blueprint(health_bp, url_prefix="/api", name="health_api")
    app.register_blueprint(chat_bp, url_prefix="/api", name="chat_api")
    app.register_blueprint(suggestions_bp, url_prefix="/api", name="suggestions_api")

    def _find_file(filename):
        candidates = [
            MAIN_PAGE_DIR / filename,
            FRONTEND_OUT_DIR / filename,
            ROOT_DIR / filename,
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.parent, candidate.name
        return None, None

    # Route: Landing page
    @app.route("/")
    @app.route("/home")
    def serve_home():
        dir_path, name = _find_file("index.html")
        if dir_path and name:
            return send_from_directory(str(dir_path), name)
        return "<h1>ARDRAXIS Web App Ready</h1><p>Running on Python Flask.</p>", 200

    # Route: D'RAX Chat Interface
    @app.route("/chat")
    @app.route("/coming_soon")
    def serve_chat():
        dir_path, name = _find_file("index.html")
        if dir_path and name:
            return send_from_directory(str(dir_path), name)
        return "<h1>D'RAX Chat Interface</h1>", 200

    # Serve JS folder
    @app.route("/js/<path:filename>")
    def serve_js(filename):
        if (MAIN_PAGE_DIR / "js" / filename).exists():
            return send_from_directory(str(MAIN_PAGE_DIR / "js"), filename)
        if (FRONTEND_OUT_DIR / "js" / filename).exists():
            return send_from_directory(str(FRONTEND_OUT_DIR / "js"), filename)
        return {"error": "JS file not found"}, 404

    # Serve static assets
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        if (MAIN_PAGE_DIR / filename).exists():
            return send_from_directory(str(MAIN_PAGE_DIR), filename)
        if (FRONTEND_OUT_DIR / filename).exists():
            return send_from_directory(str(FRONTEND_OUT_DIR), filename)
        return {"error": "Static file not found"}, 404

    # Catch-all for root files (CSS, images, HTML)
    @app.route("/<path:filename>")
    def serve_root_files(filename):
        if filename.startswith("api/"):
            return {"error": "API route not found"}, 404
        dir_path, name = _find_file(filename)
        if dir_path and name:
            return send_from_directory(str(dir_path), name)
        return {"error": f"File {filename} not found"}, 404

    @app.errorhandler(404)
    def not_found(_e):
        return {"error": "Page or endpoint not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(500)
    def internal_error(_e):
        logger.error("Internal server error", exc_info=True)
        return {"error": "Internal server error"}, 500

    logger.info("DRAX Unified Python Application initialized")
    return app


app = create_app()

if __name__ == "__main__":
    Config.validate()
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.FLASK_DEBUG)

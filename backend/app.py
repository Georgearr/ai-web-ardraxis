from flask import Flask
from config import Config
from utils.logger import logger
from middleware.security import init_security
from middleware.rate_limit import init_rate_limiter
from blueprints.health import health_bp
from blueprints.chat import chat_bp
from blueprints.suggestions import suggestions_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    init_security(app)
    init_rate_limiter(app)

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(chat_bp, url_prefix="/api/v1")
    app.register_blueprint(suggestions_bp, url_prefix="/api/v1")

    @app.errorhandler(404)
    def not_found(_e):
        return {"error": "Not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(500)
    def internal_error(_e):
        logger.error("Internal server error", exc_info=True)
        return {"error": "Internal server error"}, 500

    logger.info("DRAX API initialized")
    return app


app = create_app()

if __name__ == "__main__":
    Config.validate()
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)

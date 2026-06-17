from flask_cors import CORS
from config import Config


def init_security(app):
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [Config.FRONTEND_URL],
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type"],
            }
        },
    )

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

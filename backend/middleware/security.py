from flask_cors import CORS
from config import Config


def _allowed_origins() -> list[str]:
    origins = {Config.FRONTEND_URL.rstrip("/")}

    if Config.DEV_MODE or Config.FLASK_DEBUG:
        origins.update(
            {
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            }
        )

    return sorted(origins)


def init_security(app):
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": _allowed_origins(),
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

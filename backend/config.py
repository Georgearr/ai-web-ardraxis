import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    SHEET_MEMBERS_RANGE = "Members!A:G"
    SHEET_EVENTS_RANGE = "Events!A:F"

    @classmethod
    def validate(cls):
        errors = []
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set")
        if not cls.GOOGLE_SHEET_ID:
            errors.append("GOOGLE_SHEET_ID is not set")
        if cls.GOOGLE_SERVICE_ACCOUNT_JSON == "{}":
            errors.append("GOOGLE_SERVICE_ACCOUNT_JSON is not set")
        if errors:
            raise RuntimeError(
                "Configuration errors:\n  - " + "\n  - ".join(errors)
            )

    @classmethod
    def get_service_account_creds(cls):
        return json.loads(cls.GOOGLE_SERVICE_ACCOUNT_JSON)

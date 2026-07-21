import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    DEV_MODE = os.getenv("DEV_MODE", "0") == "1"
    PORT = int(os.getenv("PORT", "5001"))
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")

    AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
    AI_FALLBACK_ENABLED = os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"
    AI_FALLBACK_ORDER = os.getenv("AI_FALLBACK_ORDER", "deepseek,openrouter,openai,gemini")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3:free")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    @classmethod
    def use_mock_ai(cls) -> bool:
        return cls.DEV_MODE and not cls.DEEPSEEK_API_KEY and cls.AI_PROVIDER == "deepseek"

    @classmethod
    def validate(cls):
        if cls.DEV_MODE:
            return

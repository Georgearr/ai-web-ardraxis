from config import Config
from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return "Gemini"

    @property
    def default_model(self) -> str:
        return Config.GEMINI_MODEL

    @property
    def api_key(self) -> str:
        return Config.GEMINI_API_KEY

    def _build_endpoint(self) -> str:
        model = self._get_model()
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def _build_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    def _build_payload(self, messages: list[dict]) -> dict:
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] in ("user", "system") else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })
        return {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": self.temperature,
                "topP": self.top_p,
                "maxOutputTokens": self.max_tokens,
            },
        }

    def _parse_response(self, data: dict) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return ""
        return parts[0].get("text", "").strip()

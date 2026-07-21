from config import Config
from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def default_model(self) -> str:
        return Config.OPENAI_MODEL

    @property
    def api_key(self) -> str:
        return Config.OPENAI_API_KEY

    def _build_endpoint(self) -> str:
        return "https://api.openai.com/v1/chat/completions"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, messages: list[dict]) -> dict:
        return {
            "model": self._get_model(),
            "messages": messages,
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 1024,
        }

    def _parse_response(self, data: dict) -> str:
        choices = data.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "").strip()

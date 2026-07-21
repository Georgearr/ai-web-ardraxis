from config import Config
from .base_provider import BaseProvider


class DeepSeekProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return "DeepSeek"

    @property
    def default_model(self) -> str:
        return Config.DEEPSEEK_MODEL

    @property
    def api_key(self) -> str:
        return Config.DEEPSEEK_API_KEY

    def _build_endpoint(self) -> str:
        return "https://api.deepseek.com/chat/completions"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, messages: list[dict]) -> dict:
        return {
            "model": self._get_model(),
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }

    def _parse_response(self, data: dict) -> str:
        choices = data.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "").strip()

from config import Config
from utils.logger import logger
from .base_provider import BaseProvider, ProviderError


class OpenRouterProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return "OpenRouter"

    @property
    def default_model(self) -> str:
        return Config.OPENROUTER_MODEL

    @property
    def api_key(self) -> str:
        return Config.OPENROUTER_API_KEY

    def _build_endpoint(self) -> str:
        return "https://openrouter.ai/api/v1/chat/completions"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": Config.FRONTEND_URL,
            "X-Title": "DRAX AI Assistant",
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

    def ask(self, user_message: str, context: str) -> str:
        self._max_tokens_override = None

        for attempt in range(2):
            try:
                return super().ask(user_message, context)
            except ProviderError as e:
                has_credit_error = (
                    "requires more credits" in (e.reason or "").lower()
                )
                if attempt == 0 and has_credit_error and Config.AI_MAX_TOKENS > 256:
                    logger.info("Retrying OpenRouter with max_tokens=256...")
                    self._max_tokens_override = 256
                    continue
                raise

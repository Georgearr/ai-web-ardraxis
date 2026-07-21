from config import Config
from utils.logger import logger
from .base_provider import BaseProvider
from .deepseek_provider import DeepSeekProvider
from .openrouter_provider import OpenRouterProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

PROVIDER_MAP: dict[str, type[BaseProvider]] = {
    "deepseek": DeepSeekProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


class ProviderFactory:
    @staticmethod
    def create(provider_name: str | None = None) -> BaseProvider:
        name = (provider_name or Config.AI_PROVIDER).lower()
        provider_cls = PROVIDER_MAP.get(name)
        if not provider_cls:
            logger.error("Unknown AI provider: %s, falling back to deepseek", name)
            provider_cls = DeepSeekProvider
        return provider_cls()

    @staticmethod
    def get_fallback_order() -> list[str]:
        order_raw = Config.AI_FALLBACK_ORDER
        if not order_raw:
            return [Config.AI_PROVIDER.lower()]
        return [p.strip().lower() for p in order_raw.split(",") if p.strip()]

    @staticmethod
    def is_fallback_enabled() -> bool:
        return Config.AI_FALLBACK_ENABLED

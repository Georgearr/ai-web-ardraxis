from config import Config
from utils.logger import logger
from services.providers.factory import ProviderFactory
from services.providers.base_provider import ProviderError, RETRYABLE_STATUS_CODES


def ask_ai(user_message: str, context: str) -> str:
    factory = ProviderFactory()
    fallback_enabled = factory.is_fallback_enabled()
    fallback_order = factory.get_fallback_order() if fallback_enabled else [Config.AI_PROVIDER.lower()]

    last_error = None

    for idx, provider_name in enumerate(fallback_order):
        if idx > 0:
            logger.info("Switching to: %s", provider_name)
            logger.info("=" * 60)

        try:
            provider = factory.create(provider_name)
            return provider.ask(user_message, context)
        except ProviderError as e:
            last_error = e
            logger.info(
                "Provider %s FAILED — Status: %s, Reason: %s",
                provider_name,
                e.status_code or "N/A",
                e.reason,
            )

            if e.status_code is not None and e.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(
                    "Non-retryable error from %s, stopping fallback chain",
                    provider_name,
                )
                break
        except Exception as e:
            last_error = ProviderError(None, f"Unexpected error: {e}")
            logger.error("Unexpected error from %s: %s", provider_name, e)

    logger.error("All AI providers failed. Last error: %s", last_error)
    return "Maaf, AI sedang tidak tersedia. Silakan coba lagi nanti."

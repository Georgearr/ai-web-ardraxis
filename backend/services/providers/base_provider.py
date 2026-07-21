import json
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests

from config import Config
from utils.logger import logger

RETRYABLE_STATUS_CODES = {401, 402, 403, 408, 429, 500, 502, 503}


class ProviderError(Exception):
    def __init__(self, status_code: int | None, reason: str):
        self.status_code = status_code
        self.reason = reason
        super().__init__(f"[{status_code}] {reason}")


class BaseProvider(ABC):
    TIMEOUT = 60
    _max_tokens_override: int | None = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @property
    @abstractmethod
    def api_key(self) -> str:
        pass

    @abstractmethod
    def _build_endpoint(self) -> str:
        pass

    @abstractmethod
    def _build_headers(self) -> dict:
        pass

    @abstractmethod
    def _build_payload(self, messages: list[dict]) -> dict:
        pass

    @abstractmethod
    def _parse_response(self, data: dict) -> str:
        pass

    @property
    def max_tokens(self) -> int:
        if self._max_tokens_override is not None:
            return self._max_tokens_override
        return Config.AI_MAX_TOKENS

    @property
    def temperature(self) -> float:
        return Config.AI_TEMPERATURE

    @property
    def top_p(self) -> float:
        return Config.AI_TOP_P

    def _get_model(self) -> str:
        return self.default_model

    def _load_system_prompt(self) -> str:
        from pathlib import Path
        backend_dir = Path(__file__).resolve().parent.parent.parent
        prompt_path = backend_dir / "prompts" / "system_prompt.txt"
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning("system_prompt.txt not found, using default prompt")
            return (
                "You are DRAX, the official AI Assistant for OSIS SMA Ignatius Global School. "
                "Answer only using the provided data. Never hallucinate."
            )

    def _build_messages(self, user_message: str, context: str) -> list[dict]:
        system_prompt = self._load_system_prompt()
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\nPertanyaan: {user_message}"},
        ]

    def ask(self, user_message: str, context: str) -> str:
        api_key = self.api_key
        if not api_key:
            raise ProviderError(None, f"{self.provider_name} API key is empty")

        model = self._get_model()
        messages = self._build_messages(user_message, context)
        endpoint = self._build_endpoint()
        headers = self._build_headers()
        payload = self._build_payload(messages)

        timestamp = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()

        logger.info("=" * 60)
        logger.info("Trying Provider:   %s", self.provider_name)
        logger.info("Model:             %s", model)
        logger.info("Temperature:       %s", self.temperature)
        logger.info("Top P:             %s", self.top_p)
        logger.info("Max Tokens:        %s", self.max_tokens)
        logger.info("Request at:        %s", timestamp)

        try:
            logger.info("Calling %s API ...", self.provider_name)
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT,
            )

            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.info("%s HTTP %d (%d ms)", self.provider_name, response.status_code, latency_ms)

            if response.status_code in RETRYABLE_STATUS_CODES:
                reason = f"HTTP {response.status_code}"
                try:
                    body = response.json()
                    if "error" in body:
                        err = body["error"]
                        if isinstance(err, dict):
                            reason = err.get("message", reason)
                        elif isinstance(err, str):
                            reason = err
                except (json.JSONDecodeError, TypeError):
                    pass
                logger.error("=" * 60)
                logger.error("Provider:    %s", self.provider_name)
                logger.error("Model:       %s", model)
                logger.error("Status:      FAILED")
                logger.error("Reason:      %s", reason)
                logger.error("Latency:     %d ms", latency_ms)
                logger.error("=" * 60)
                raise ProviderError(response.status_code, reason)

            if response.status_code != 200:
                logger.error("%s unexpected HTTP %d: %s", self.provider_name, response.status_code, response.text)
                logger.error("=" * 60)
                logger.error("Provider:    %s", self.provider_name)
                logger.error("Model:       %s", model)
                logger.error("Status:      FAILED")
                logger.error("Reason:      HTTP %d", response.status_code)
                logger.error("Latency:     %d ms", latency_ms)
                logger.error("=" * 60)
                raise ProviderError(response.status_code, f"HTTP {response.status_code}")

            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error("Invalid JSON from %s: %s", self.provider_name, response.text)
                logger.error("=" * 60)
                logger.error("Provider:    %s", self.provider_name)
                logger.error("Model:       %s", model)
                logger.error("Status:      FAILED")
                logger.error("Reason:      Invalid JSON response")
                logger.error("Latency:     %d ms", latency_ms)
                logger.error("=" * 60)
                raise ProviderError(None, "Invalid JSON response")

            text = self._parse_response(data)
            if not text:
                logger.error("Empty response from %s", self.provider_name)
                raise ProviderError(None, "Empty response")

            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.info("Status:            SUCCESS")
            logger.info("Latency:           %d ms", latency_ms)
            logger.info("Response len:      %d chars", len(text))
            logger.info("Response preview:  %.200s", text)
            logger.info("=" * 60)

            usage = data.get("usage", {})
            if usage:
                logger.info("Tokens - prompt: %s, completion: %s, total: %s",
                            usage.get("prompt_tokens", "?"),
                            usage.get("completion_tokens", "?"),
                            usage.get("total_tokens", "?"))

            return text

        except requests.exceptions.Timeout:
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.error("=" * 60)
            logger.error("Provider:    %s", self.provider_name)
            logger.error("Model:       %s", model)
            logger.error("Status:      FAILED")
            logger.error("Reason:      Timeout after %d ms", latency_ms)
            logger.error("=" * 60)
            raise ProviderError(None, "Timeout")

        except requests.exceptions.ConnectionError:
            logger.error("=" * 60)
            logger.error("Provider:    %s", self.provider_name)
            logger.error("Model:       %s", model)
            logger.error("Status:      FAILED")
            logger.error("Reason:      Network Error")
            logger.error("=" * 60)
            raise ProviderError(None, "Network Error")

        except ProviderError:
            raise

        except Exception as e:
            logger.error("=" * 60)
            logger.error("Provider:    %s", self.provider_name)
            logger.error("Model:       %s", model)
            logger.error("Status:      FAILED")
            logger.error("Reason:      %s: %s", type(e).__name__, e)
            logger.error("Traceback:\n%s", traceback.format_exc())
            logger.error("=" * 60)
            raise ProviderError(None, f"{type(e).__name__}: {e}")

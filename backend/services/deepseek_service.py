import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import Config
from utils.logger import logger

BACKEND_DIR = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = BACKEND_DIR / "prompts" / "system_prompt.txt"


def _load_system_prompt() -> str:
    try:
        with open(SYSTEM_PROMPT_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning("system_prompt.txt not found, using default prompt")
        return (
            "You are DRAX, the official AI Assistant for OSIS SMA Ignatius Global School. "
            "Answer only using the provided data. Never hallucinate."
        )


SYSTEM_PROMPT = _load_system_prompt()


def ask_deepseek(user_message: str, context: str) -> str:
    api_key = Config.DEEPSEEK_API_KEY
    if not api_key:
        logger.error("DeepSeek API key is empty — cannot call DeepSeek")
        return "Maaf, AI sedang tidak tersedia. Silakan coba lagi nanti."

    model = Config.DEEPSEEK_MODEL
    timestamp = datetime.now(timezone.utc).isoformat()
    prompt_len = len(SYSTEM_PROMPT) + len(context) + len(user_message)

    logger.info("=" * 60)
    logger.info("Provider:     DeepSeek")
    logger.info("Model:        %s", model)
    logger.info("Request at:   %s", timestamp)
    logger.info("Prompt len:   %d chars", prompt_len)
    logger.info("System len:   %d chars", len(SYSTEM_PROMPT))
    logger.info("Context len:  %d chars", len(context))
    logger.info("User len:     %d chars", len(user_message))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{context}\n\nPertanyaan: {user_message}"},
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.info("Calling DeepSeek API ...")
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        logger.info("DeepSeek HTTP %d", response.status_code)

        if response.status_code != 200:
            logger.error("=" * 60)
            logger.error("DeepSeek API FAILED at %s", timestamp)
            logger.error("HTTP Status: %d", response.status_code)
            logger.error("Response body: %s", response.text)
            logger.info("=" * 60)

            if response.status_code in (401, 403):
                logger.error("Authentication/authorization error")
            elif response.status_code == 429:
                logger.error("Rate limited")
            elif response.status_code in (502, 503):
                logger.error("Service unavailable")

            return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."

        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error("Invalid JSON from DeepSeek: %s", response.text)
            return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."

        choices = data.get("choices", [])
        if not choices:
            logger.error("No choices in DeepSeek response: %s", data)
            return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            finish_reason = choices[0].get("finish_reason", "unknown")
            logger.error("Empty content (finish_reason=%s)", finish_reason)
            return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."

        text = content.strip()

        usage = data.get("usage", {})
        logger.info("Response len: %d chars", len(text))
        logger.info("Response preview: %.200s", text)
        if usage:
            logger.info("Tokens - prompt: %s, completion: %s, total: %s",
                        usage.get("prompt_tokens", "?"),
                        usage.get("completion_tokens", "?"),
                        usage.get("total_tokens", "?"))
        logger.info("=" * 60)

        return text

    except requests.exceptions.Timeout:
        logger.error("DeepSeek API TIMEOUT at %s", timestamp)
        logger.info("=" * 60)
        return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."
    except requests.exceptions.ConnectionError:
        logger.error("DeepSeek API NETWORK ERROR at %s", timestamp)
        logger.info("=" * 60)
        return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."
    except Exception as e:
        logger.error("=" * 60)
        logger.error("DeepSeek API FAILED at %s", timestamp)
        logger.error("Exception: %s: %s", type(e).__name__, e)
        logger.error("Traceback:\n%s", traceback.format_exc())
        logger.info("=" * 60)
        return "Maaf, AI sedang mengalami gangguan. Silakan coba lagi beberapa saat."

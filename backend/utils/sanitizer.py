import re


def sanitize_message(message: str) -> str:
    cleaned = re.sub(r"<[^>]*>", "", message)
    cleaned = cleaned.strip()
    if not cleaned:
        raise ValueError("Message cannot be empty")
    if len(cleaned) > 2000:
        cleaned = cleaned[:2000]
    return cleaned

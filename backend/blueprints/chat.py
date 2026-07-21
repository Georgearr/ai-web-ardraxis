import re
from pathlib import Path

from flask import Blueprint, request, jsonify
from utils.sanitizer import sanitize_message
from utils.logger import logger
from services.semantic_service import find_sekbids
from services.csv_service import csv_store
from services.ai_service import ask_ai
from services.intent_service import (
    Intent,
    detect_intent,
    process_intent,
    build_intent_context,
)
from services.session_service import session_store

BACKEND_DIR = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = BACKEND_DIR / "prompts" / "system_prompt.txt"


def _load_system_prompt() -> str:
    try:
        with open(SYSTEM_PROMPT_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are DRAX, AI Assistant for OSIS SMA Ignatius Global School."


SYSTEM_PROMPT = _load_system_prompt()


def _log_prompt_metrics(context: str, user_message: str):
    total_chars = len(SYSTEM_PROMPT) + len(context) + len(user_message)
    estimated_tokens = total_chars // 4
    context_lines = len(context.splitlines()) if context else 0
    logger.info("Prompt chars:       %d", total_chars)
    logger.info("Prompt tokens (est): %d", estimated_tokens)
    logger.info("Context chars:       %d", len(context))
    logger.info("Context items:       %d", context_lines)


def _log_final_context(context: str):
    if not context:
        return
    logger.info("=" * 60)
    logger.info("FINAL CONTEXT")
    logger.info("=" * 60)
    for line in context.splitlines():
        logger.info(line)
    logger.info("=" * 60)


_FOLLOWUP_PATTERNS = [
    r"\binstagram(nya)?\b",
    r"\big\b",
    r"\bjabatannya?\b",
    r"\bsekbidnya\b",
    r"\bsub\s*sekbid(nya)?\b",
    r"\bketua\s*pelaksana(nya)?\b",
    r"\bwakil(nya)?\b",
    r"\btanggal(nya)?\b",
    r"\blokasi(nya)?\b",
    r"\bdeskripsi(nya)?\b",
    r"\bdivisi(nya)?\b",
    r"\bdetail(nya)?\b",
    r"\bketuanya\b",
    r"\bliat\s*instagram",
    r"\bceritain\b",
    r"\binfo\s*lebih\b",
    r"\blebih\s*detail\b",
    r"\bwa\b",
    r"\bwhatsapp\b",
    r"\btelpon(nya)?\b",
    r"\bnomor(nya)?\b",
]

_SHORT_WORD_THRESHOLD = 2


def _is_followup(message: str) -> bool:
    msg = message.lower().strip()
    for pat in _FOLLOWUP_PATTERNS:
        if re.search(pat, msg):
            return True
    words = msg.split()
    if len(words) < _SHORT_WORD_THRESHOLD:
        return True
    return False


def _get_session_id() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _extract_entity(result: dict) -> str:
    matched = result.get("matched", [])
    if matched:
        first = matched[0]
        if hasattr(first, "nama_lengkap"):
            return first.nama_lengkap
        if hasattr(first, "nama_event"):
            return first.nama_event
        if hasattr(first, "nama_program"):
            return first.nama_program
        if hasattr(first, "pertanyaan"):
            return first.pertanyaan
    return ""


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        raw_message = data.get("message", "")
        message = sanitize_message(raw_message)

        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        logger.info("Processing message: %.100s", message)
        session_id = _get_session_id()

        if _is_followup(message):
            stored_context = session_store.get_last_context(session_id)
            if stored_context is not None:
                logger.info(
                    "[SESSION] Follow-up detected, using stored context"
                )
                context = stored_context
                _log_final_context(context)
                _log_prompt_metrics(context, message)
                response = ask_ai(message, context)
                logger.info(
                    "Response generated (len=%d, session_reuse=True)",
                    len(response),
                )
                return jsonify({"response": response}), 200

        member_models = csv_store.get_members()
        event_models = csv_store.get_events()
        faq_models = csv_store.get_faqs()
        program_models = csv_store.get_programs()

        matched_sekbids = find_sekbids(message)

        intent = detect_intent(message)

        if intent == Intent.UNKNOWN and matched_sekbids:
            intent = Intent.MEMBER_SEARCH

        logger.info("Detected intent: %s", intent.value)

        result = process_intent(
            intent, message,
            member_models, event_models, faq_models, program_models,
            matched_sekbids,
        )

        context = build_intent_context(result)

        if context:
            entity = _extract_entity(result)
            session_store.save(
                session_id,
                context=context,
                intent=intent.value,
                entity=entity,
            )

        _log_final_context(context)
        _log_prompt_metrics(context, message)
        response = ask_ai(message, context)

        logger.info(
            "Response generated (len=%d, intent=%s, matched_sekbids=%s)",
            len(response),
            intent.value,
            matched_sekbids,
        )

        return jsonify({"response": response}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Chat error: %s", e, exc_info=True)
        return jsonify({"error": "Terjadi kesalahan internal server."}), 500

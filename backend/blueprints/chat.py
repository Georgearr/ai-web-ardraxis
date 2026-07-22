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
    has_sekbid_mention,
    is_special_faq_query,
    _detect_responsibility,
    _detect_entity_mention,
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

_MEMBER_FOLLOWUP_PATTERNS = [
    r"\bsiapa\s*saja\b",
    r"\banggotanya\b",
    r"\banggota\s*lain\b",
    r"\bsemuanya\b",
    r"\blist\s*anggota\b",
    r"\bdaftar\s*anggota\b",
    r"\btampilkan\s*semua\b",
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


def _is_member_followup(message: str) -> bool:
    msg = message.lower().strip()
    if _is_followup(msg):
        return True
    for pat in _MEMBER_FOLLOWUP_PATTERNS:
        if re.search(pat, msg):
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

        # -----------------------------------------------------------------------
        # FOLLOW-UP PATH – reuse last_sekbid if user asks about members generically
        # -----------------------------------------------------------------------
        if _is_member_followup(message) and not is_special_faq_query(message) and not has_sekbid_mention(message) and not find_sekbids(message):
            last_sekbid = session_store.get_last_sekbid(session_id)
            if last_sekbid:
                logger.info("[SESSION] Using previous sekbid context: %s", last_sekbid)
                member_models = csv_store.get_members()
                event_models = csv_store.get_events()
                faq_models = csv_store.get_faqs()
                program_models = csv_store.get_programs()
                result = process_intent(
                    Intent.MEMBER_SEARCH, message,
                    member_models, event_models, faq_models, program_models,
                    matched_sekbids=[last_sekbid],
                )
                context = build_intent_context(result)
                if context:
                    _log_member_retrieval(message, result)
                    _log_final_context(context)
                    _log_prompt_metrics(context, message)
                    _save_session(session_id, result, context, matched_sekbids=[last_sekbid])
                    response = ask_ai(message, context)
                    return jsonify({"response": response}), 200

        # -----------------------------------------------------------------------
        # NORMAL FOLLOW-UP (Instagram, detail, etc.) – reuse stored context
        # -----------------------------------------------------------------------
        if _is_followup(message):
            stored_context = session_store.get_last_context(session_id)
            if stored_context is not None:
                logger.info("[SESSION] Follow-up detected, using stored context")
                _log_final_context(stored_context)
                _log_prompt_metrics(stored_context, message)
                response = ask_ai(message, stored_context)
                logger.info(
                    "Response generated (len=%d, session_reuse=True)",
                    len(response),
                )
                return jsonify({"response": response}), 200

        # -----------------------------------------------------------------------
        # FRESH QUERY PATH
        # -----------------------------------------------------------------------
        member_models = csv_store.get_members()
        event_models = csv_store.get_events()
        faq_models = csv_store.get_faqs()
        program_models = csv_store.get_programs()

        matched_sekbids = find_sekbids(message)

        # --- FAQ-FIRST CASCADE (highest priority) ---
        faq_result = process_intent(
            Intent.FAQ, message,
            member_models, event_models, faq_models, program_models,
            matched_sekbids,
        )
        if faq_result.get("matched"):
            # Guard: if query asks about members ("anggota") but the matched
            # FAQ doesn't contain "anggota", skip FAQ – the query is about
            # membership, not the FAQ topic.
            faq = faq_result["matched"][0]
            faq_text = (faq.pertanyaan + " " + faq.jawaban).lower()
            msg_lower = message.lower()
            if "anggota" in msg_lower and "anggota" not in faq_text:
                logger.info("FAQ matched but query asks about members – skipping FAQ")
                faq_result = {"matched": []}
            else:
                logger.info("FAQ matched: YES / Skip member retrieval")
                context = build_intent_context(faq_result)
                _log_faq_retrieval(message, faq_result)
                _log_final_context(context)
                _log_prompt_metrics(context, message)
                _save_session(session_id, faq_result, context, matched_sekbids=matched_sekbids)
                response = ask_ai(message, context)
                return jsonify({"response": response}), 200

        logger.info("FAQ matched: NO / Continue member retrieval")

        # SPECIAL FAQ takes priority over every other intent
        if is_special_faq_query(message):
            logger.info("Special FAQ query detected – overriding intent to FAQ")
            intent = Intent.FAQ
        else:
            intent = detect_intent(message)

        # Unknown + sekbid mention → member search (unless special FAQ already matched)
        if intent == Intent.UNKNOWN and (matched_sekbids or has_sekbid_mention(message)):
            if not is_special_faq_query(message):
                intent = Intent.MEMBER_SEARCH

        # Entity‑mention preprocessing – if message contains a known member
        # identity, force MEMBER_SEARCH and skip the FAQ classifier entirely.
        entity_type = _detect_entity_mention(message, member_models)
        if entity_type and intent in (Intent.FAQ, Intent.UNKNOWN):
            # Only override FAQ for personal matches (name/nickname/instagram/
            # alias).  Broad divisional matches (sekbid/position) that happen
            # to appear in a FAQ question must NOT hijack the FAQ intent.
            if intent == Intent.FAQ and entity_type in ("position", "sekbid"):
                logger.info("Entity mention=%s but intent is FAQ – keeping FAQ", entity_type)
            else:
                logger.info("Entity mention detected: %s – overriding to MEMBER_SEARCH", entity_type)
                intent = Intent.MEMBER_SEARCH

        # Responsibility query overrides member/list/event/program intents –
        # structural sekbid answer instead of person/event/program listing.
        resp_match = _detect_responsibility(message, member_models)
        if intent in (Intent.MEMBER_SEARCH, Intent.LIST_MEMBERS,
                      Intent.EVENT_SEARCH, Intent.PROGRAM_SEARCH) and resp_match:
            # Keep person-level intent when:
            # 1) Query matched a specific individual (full name, nickname, Instagram, alias)
            if entity_type and entity_type in ("fullname", "nickname", "instagram", "alias"):
                logger.info("Personal entity mention=%s – keeping %s",
                            entity_type, intent.value)
            # 2) Query asks about a specific leadership role (koordinator, ketua, etc.)
            #    rather than a division/membership question.
            elif any(re.search(r'\b' + re.escape(r) + r'\b', message.lower())
                     for r in ("koordinator", "ketua", "wakil ketua",
                               "sekretaris", "bendahara")):
                logger.info("Specific role query – keeping %s", intent.value)
            else:
                logger.info("Responsibility query detected – overriding to RESPONSIBILITY")
                intent = Intent.RESPONSIBILITY

        logger.info("Detected intent: %s", intent.value)

        result = process_intent(
            intent, message,
            member_models, event_models, faq_models, program_models,
            matched_sekbids,
        )

        context = build_intent_context(result)

        # Intent‑aware logging – never access Member attributes on non‑Member objects
        if intent in (Intent.MEMBER_SEARCH, Intent.LIST_MEMBERS):
            _log_member_retrieval(message, result)
        elif intent == Intent.RESPONSIBILITY:
            _log_member_retrieval(message, result)
        elif intent == Intent.FAQ:
            _log_faq_retrieval(message, result)
        elif intent == Intent.EVENT_SEARCH:
            _log_event_retrieval(message, result)
        elif intent == Intent.PROGRAM_SEARCH:
            _log_program_retrieval(message, result)

        if context:
            _save_session(session_id, result, context, matched_sekbids=matched_sekbids)

        _log_final_context(context)
        _log_prompt_metrics(context, message)

        if not context:
            fallback = "Maaf, saya belum menemukan informasi tersebut pada database resmi ARDRAXIS."
            return jsonify({"response": fallback}), 200

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


def _extract_sekbid_from_result(result: dict, matched_sekbids: list[str] | None = None) -> str:
    if matched_sekbids:
        return matched_sekbids[0]
    matched = result.get("matched", [])
    if matched and hasattr(matched[0], "sekbid"):
        if matched[0].sub_sekbid:
            return matched[0].sub_sekbid
        return matched[0].sekbid
    return ""


def _extract_member_from_result(result: dict) -> str:
    matched = result.get("matched", [])
    if matched and hasattr(matched[0], "nama_lengkap"):
        return matched[0].nama_lengkap
    return ""


def _extract_event_from_result(result: dict) -> str:
    matched = result.get("matched", [])
    if matched and hasattr(matched[0], "nama_event"):
        return matched[0].nama_event
    return ""


def _save_session(session_id: str, result: dict, context: str, matched_sekbids: list[str] | None = None):
    entity = _extract_entity(result)
    last_sekbid = _extract_sekbid_from_result(result, matched_sekbids)
    last_member = _extract_member_from_result(result)
    last_event = _extract_event_from_result(result)
    session_store.save(
        session_id,
        context=context,
        intent=result.get("intent", Intent.UNKNOWN).value if isinstance(result.get("intent"), Intent) else str(result.get("intent", "")),
        entity=entity,
        last_member=last_member,
        last_sekbid=last_sekbid,
        last_event=last_event,
    )


def _log_member_retrieval(message: str, result: dict):
    matched = result.get("matched", [])
    intent = result.get("intent")
    # Safety guard – never assume matched items are Member objects
    if intent is not None and intent not in (Intent.MEMBER_SEARCH, Intent.LIST_MEMBERS):
        logger.warning("_log_member_retrieval called with intent=%s – skipping", intent)
        return
    logger.info("=== MEMBER RETRIEVAL ===")
    logger.info("Query           : %s", message)
    logger.info("Matched members : %d", len(matched))
    if matched:
        for m in matched:
            if not hasattr(m, "nama_lengkap"):
                logger.warning("Non‑Member object in matched list: %s", type(m).__name__)
                continue
            logger.info(
                "- %s | %s | %s | %s",
                m.nama_lengkap,
                m.jabatan,
                m.sekbid,
                m.sub_sekbid or "-",
            )
    logger.info("=" * 50)


def _log_faq_retrieval(message: str, result: dict):
    matched = result.get("matched", [])
    logger.info("=== FAQ RETRIEVAL ===")
    logger.info("Query      : %s", message)
    logger.info("FAQ matched: %d", len(matched))
    for faq in matched:
        if hasattr(faq, "pertanyaan") and hasattr(faq, "jawaban"):
            logger.info("Q: %s", faq.pertanyaan)
            logger.info("A: %s", faq.jawaban[:200] if faq.jawaban else "(empty)")
    logger.info("=" * 50)


def _log_event_retrieval(message: str, result: dict):
    matched = result.get("matched", [])
    logger.info("=== EVENT RETRIEVAL ===")
    logger.info("Query       : %s", message)
    logger.info("Events found: %d", len(matched))
    for ev in matched:
        if hasattr(ev, "nama_event"):
            logger.info("- %s", ev.nama_event)
    logger.info("=" * 50)


def _log_program_retrieval(message: str, result: dict):
    matched = result.get("matched", [])
    logger.info("=== PROGRAM RETRIEVAL ===")
    logger.info("Query         : %s", message)
    logger.info("Programs found: %d", len(matched))
    for p in matched:
        if hasattr(p, "nama_program"):
            logger.info("- %s", p.nama_program)
    logger.info("=" * 50)

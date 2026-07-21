from flask import Blueprint, request, jsonify
from utils.sanitizer import sanitize_message
from utils.logger import logger
from services.semantic_service import find_sekbids
from services.csv_service import csv_store
from services.gemini_service import build_context
from services.ai_service import ask_ai
from services.intent_service import (
    Intent,
    detect_intent,
    process_intent,
    build_intent_context,
)

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

        member_models = csv_store.get_members()
        event_models = csv_store.get_events()
        faq_models = csv_store.get_faqs()
        program_models = csv_store.get_programs()

        members = [m.to_dict() for m in member_models]
        events = [e.to_dict() for e in event_models]
        faqs = [f.to_dict() for f in faq_models]
        programs = [p.to_dict() for p in program_models]

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
        if not context:
            context = build_context(members, events, faqs, programs, matched_sekbids)
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

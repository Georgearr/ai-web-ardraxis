from flask import Blueprint, request, jsonify
from utils.sanitizer import sanitize_message
from utils.logger import logger
from services.semantic_service import find_sekbids
from services.sheet_service import get_members, get_events
from config import Config
from services.gemini_service import init_gemini, build_context, ask_gemini
from services.mock_service import mock_ai_response

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

        member_models = get_members()
        event_models = get_events()
        members = [m.to_dict() for m in member_models]
        events = [e.to_dict() for e in event_models]

        matched_sekbids = find_sekbids(message)

        if Config.use_mock_ai():
            response = mock_ai_response(message, member_models, event_models)
        else:
            context = build_context(members, events, matched_sekbids)
            init_gemini()
            response = ask_gemini(message, context)

        logger.info(
            "Response generated (len=%d, matched_sekbids=%s)",
            len(response),
            matched_sekbids,
        )

        return jsonify({"response": response}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Chat error: %s", e, exc_info=True)
        return jsonify({"error": "Terjadi kesalahan internal server."}), 500

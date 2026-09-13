from flask import Blueprint, jsonify

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

suggestions_bp = Blueprint("suggestions", __name__)

SUGGESTIONS = [
    "Siapa Ketua OSIS?",
    "Siapa yang mengurus website?",
    "Apa itu ARDRAXIS?",
]

# Helper to filter suggestions based on backend support
def get_valid_suggestions():
    """Return only suggestions that have a corresponding backend intent.
    A suggestion is considered valid if the intent detection identifies a known intent
    (i.e., not UNKNOWN) or the text mentions a sekbid keyword or a special FAQ pattern.
    """
    from services.intent_service import detect_intent, has_sekbid_mention, is_special_faq_query, Intent
    valid = []
    for s in SUGGESTIONS:
        intent = detect_intent(s)
        if intent != Intent.UNKNOWN or has_sekbid_mention(s) or is_special_faq_query(s):
            valid.append(s)
        else:
            # Log the dropped suggestion for debugging
            from utils.logger import logger
            logger.debug("Dropping suggestion without backend support: %s", s)
    return valid


@suggestions_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    # Return the filtered suggestion list
    return jsonify({"suggestions": get_valid_suggestions()}), 200

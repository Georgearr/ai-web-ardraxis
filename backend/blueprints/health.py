from flask import Blueprint, jsonify
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "DRAX API",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ), 200

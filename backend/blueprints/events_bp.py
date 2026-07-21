from flask import Blueprint, jsonify
from services.csv_service import csv_store
from utils.logger import logger

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def get_events():
    try:
        events = csv_store.get_events()
        data = [e.to_dict() for e in events]
        logger.info("Events endpoint: returned %d events", len(data))
        return jsonify({"events": data}), 200
    except Exception as e:
        logger.error("Events endpoint error: %s", e, exc_info=True)
        return jsonify({"error": "Terjadi kesalahan internal server."}), 500

from flask import Blueprint, jsonify
from services.csv_service import csv_store
from utils.logger import logger

members_bp = Blueprint("members", __name__)


@members_bp.route("/members", methods=["GET"])
def get_members():
    try:
        members = csv_store.get_members()
        data = [m.to_dict() for m in members]
        logger.info("Members endpoint: returned %d members", len(data))
        return jsonify({"members": data}), 200
    except Exception as e:
        logger.error("Members endpoint error: %s", e, exc_info=True)
        return jsonify({"error": "Terjadi kesalahan internal server."}), 500

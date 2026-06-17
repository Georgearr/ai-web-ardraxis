from flask import Blueprint, jsonify

suggestions_bp = Blueprint("suggestions", __name__)

SUGGESTIONS = [
    "Siapa Ketua OSIS?",
    "Event terdekat apa?",
    "Siapa yang mengurus website?",
    "Siapa yang mengurus Instagram?",
    "Apa tugas Governance?",
    "Siapa koordinator Multimedia Website?",
    "Berapa jumlah anggota OSIS?",
    "Apa Instagram OSIS?",
]


@suggestions_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    return jsonify({"suggestions": SUGGESTIONS}), 200

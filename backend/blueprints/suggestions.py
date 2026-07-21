from flask import Blueprint, jsonify

suggestions_bp = Blueprint("suggestions", __name__)

SUGGESTIONS = [
    "Siapa Ketua OSIS?",
    "Event terdekat apa?",
    "Siapa yang mengurus website?",
    "Siapa yang mengurus Instagram?",
    "Apa itu ARDRAXIS?",
    "Siapa koordinator Multimedia Website?",
    "Program kerja apa saja?",
    "Apa Instagram OSIS?",
    "Apa saja sekbid di ARDRAXIS?",
    "Siapa Wakil Ketua OSIS?",
]


@suggestions_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    return jsonify({"suggestions": SUGGESTIONS}), 200

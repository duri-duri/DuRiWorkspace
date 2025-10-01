from flask import Blueprint, jsonify, request

decision_input_bp = Blueprint("decision_input", __name__)


@decision_input_bp.route("/decision", methods=["POST"])
def receive_decision():
    data = request.get_json()
    return jsonify({"status": "received", "data": data})

#!/usr/bin/env python3
import json
import os
from datetime import datetime

from flask import Flask, jsonify, request

EVOLUTION_LOG = "/data/evolution_data/evolution_log.json"


def get_recent_result_for(emotion):
    """가장 최근 해당 감정의 결과를 찾는다"""
    if not os.path.exists(EVOLUTION_LOG):
        return None
    try:
        with open(EVOLUTION_LOG, "r") as f:
            logs = json.load(f)
    except:
        return None

    for entry in reversed(logs):
        exp = entry.get("experience", {})
        if exp.get("emotion") == emotion:
            return exp.get("result")
    return None


app = Flask(__name__)


@app.route("/brain", methods=["POST"])
def brain_decision():
    try:
        data = request.get_json(force=True)
        emotion = data.get("emotion", "unknown")
        result = get_recent_result_for(emotion)

        # 기억 기반 판단 변경
        if result == "fail":
            decision = {"action": "wait", "confidence": 0.5}
        else:
            decision = {"action": "reflect", "confidence": 0.95}

        return jsonify({"decision": decision})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    app.run(host="0.0.0.0", port=port)

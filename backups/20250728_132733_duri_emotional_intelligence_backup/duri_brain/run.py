import os
from duri_brain.app import create_app
from flask import Flask, jsonify

app = create_app()

@app.route("/")
def index():
    return jsonify({"message": "Welcome to Brain Service!"})

@app.route("/brain", methods=["POST"])
def brain_decision():
    return jsonify({"decision": "some decision"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    app.run(host="0.0.0.0", port=port)

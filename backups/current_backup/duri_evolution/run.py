import os
from duri_evolution.app import create_app
from flask import Flask, jsonify

app = create_app()

@app.route("/")
def index():
    return jsonify({"message": "Welcome to Evolution Service!"})

@app.route("/evolve", methods=["POST"])
def evolve():
    return jsonify({"evolution": "some evolution"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8082))
    app.run(host="0.0.0.0", port=port)

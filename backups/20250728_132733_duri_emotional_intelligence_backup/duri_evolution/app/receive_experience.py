from flask import Blueprint, request, jsonify
import os, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

experience_bp = Blueprint("experience", __name__)

LOG_DIR = os.getenv("LOG_DIR", "./logs")
EVOLUTION_DIR = os.getenv("EVOLUTION_DIR", "./evolution_data")
EVOLUTION_LOG = os.getenv("EVOLUTION_LOG", "./evolution_data/evolution_log.json")
LOG_FILE = os.path.join(LOG_DIR, "evolution_receive.log")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EVOLUTION_DIR, exist_ok=True)

def append_evolution_log(entry):
    logs = []
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(EVOLUTION_LOG, "w") as f:
        json.dump(logs[-1000:], f, indent=2, ensure_ascii=False)

@experience_bp.route("/", methods=["POST"])
def receive_experience():
    try:
        data = request.get_json(force=True)
        now = datetime.now().isoformat()
        with open(LOG_FILE, "a") as f:
            f.write(f"{now} :: RECEIVED :: {json.dumps(data, ensure_ascii=False)}\n")
        append_evolution_log({"timestamp": now, "experience": data})
        return jsonify({"status": "stored", "timestamp": now})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "detail": str(e)}), 500

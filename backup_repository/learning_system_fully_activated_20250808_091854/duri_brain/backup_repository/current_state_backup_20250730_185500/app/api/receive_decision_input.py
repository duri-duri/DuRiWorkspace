# duri_brain/app/api/receive_decision_input.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 환경 변수
LOG_DIR = os.getenv("LOG_DIR", "./logs")
STATE_DIR = os.getenv("STATE_DIR", "./brain_state")
DECISION_LOG = os.getenv("DECISION_LOG", "./brain_state/decision_log.json")

# 디렉토리 보장
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# 로그 파일 경로
LOG_FILE = os.path.join(LOG_DIR, "brain_receive.log")

# APIRouter 선언
router = APIRouter()

def append_decision_log(entry):
    logs = []
    if os.path.exists(DECISION_LOG):
        with open(DECISION_LOG, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(DECISION_LOG, "w") as f:
        json.dump(logs[-500:], f, indent=2, ensure_ascii=False)

@router.post("/")
async def receive_brain_input(request: Request):
    try:
        data = await request.json()
        now = datetime.now().isoformat()

        log_line = f"{now} :: RECEIVED :: {json.dumps(data, ensure_ascii=False)}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_line)

        decision = {"action": "reflect", "confidence": 0.95}

        append_decision_log({
            "timestamp": now,
            "input": data,
            "decision": decision
        })

        return JSONResponse(content={"decision": decision, "timestamp": now})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

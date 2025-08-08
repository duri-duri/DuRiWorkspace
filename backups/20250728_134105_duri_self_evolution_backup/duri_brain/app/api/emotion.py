# app/api/emotion.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import json, os

router = APIRouter()

LOG_FILE = "./../logs/emotion.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

@router.post("/")
async def handle_emotion(request: Request):
    data = await request.json()
    timestamp = datetime.now().isoformat()

    log_line = f"{timestamp} :: EMOTION :: {json.dumps(data, ensure_ascii=False)}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

    return JSONResponse(content={"status": "received", "timestamp": timestamp})

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ProcessInput(BaseModel):
    input: str

class ProcessOutput(BaseModel):
    status: str
    message: str
    data: dict
    timestamp: str

@router.post("/", response_model=ProcessOutput)
async def process_handler(payload: ProcessInput):
    user_input = payload.input.strip().lower()

    if not user_input:
        raise HTTPException(status_code=400, detail="입력이 비어 있습니다")

    # 예시 분석 로직
    if "reflect" in user_input:
        action = "reflect"
        explanation = "입력에 'reflect' 키워드가 포함되어 있습니다. 반성 동작을 추천합니다."
    elif "think" in user_input:
        action = "analyze"
        explanation = "생각 관련 입력이 감지되어 분석 동작을 추천합니다."
    else:
        action = "store"
        explanation = "입력이 특이하지 않아 일반 저장 동작을 수행합니다."

    response = {
        "status": "success",
        "message": "입력 처리 완료",
        "data": {
            "action": action,
            "explanation": explanation
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    return response

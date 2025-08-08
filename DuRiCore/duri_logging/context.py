#!/usr/bin/env python3
"""
DuRi 컨텍스트 전파 시스템

요청/세션/학습 세션 ID와 단계를 전파합니다.
"""

from contextvars import ContextVar
from typing import Dict, Optional
import uuid

# 컨텍스트 변수들
_request_id = ContextVar("request_id", default="-")
_session_id = ContextVar("session_id", default="-")
_learning_session_id = ContextVar("learning_session_id", default="-")
_phase = ContextVar("phase", default="-")

def set_request_id(value: str) -> None:
    """요청 ID를 설정합니다."""
    _request_id.set(value)

def set_session_id(value: str) -> None:
    """세션 ID를 설정합니다."""
    _session_id.set(value)

def set_learning_session_id(value: str) -> None:
    """학습 세션 ID를 설정합니다."""
    _learning_session_id.set(value)

def set_phase(value: str) -> None:
    """학습 단계를 설정합니다."""
    _phase.set(value)

def get_request_id() -> str:
    """현재 요청 ID를 반환합니다."""
    return _request_id.get()

def get_session_id() -> str:
    """현재 세션 ID를 반환합니다."""
    return _session_id.get()

def get_learning_session_id() -> str:
    """현재 학습 세션 ID를 반환합니다."""
    return _learning_session_id.get()

def get_phase() -> str:
    """현재 학습 단계를 반환합니다."""
    return _phase.get()

def get_context() -> Dict[str, str]:
    """현재 컨텍스트를 딕셔너리로 반환합니다."""
    return {
        "request_id": _request_id.get(),
        "session_id": _session_id.get(),
        "learning_session_id": _learning_session_id.get(),
        "phase": _phase.get()
    }

def clear_context() -> None:
    """컨텍스트를 초기화합니다."""
    _request_id.set("-")
    _session_id.set("-")
    _learning_session_id.set("-")
    _phase.set("-")

def generate_request_id() -> str:
    """새로운 요청 ID를 생성합니다."""
    return str(uuid.uuid4())[:8]

def generate_session_id() -> str:
    """새로운 세션 ID를 생성합니다."""
    return str(uuid.uuid4())[:12]

def generate_learning_session_id() -> str:
    """새로운 학습 세션 ID를 생성합니다."""
    return f"learn_{str(uuid.uuid4())[:8]}"

# FastAPI 미들웨어 (선택적)
def fastapi_middleware():
    """FastAPI 미들웨어를 생성합니다."""
    try:
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.requests import Request
        from starlette.responses import Response
        
        class CorrelationMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # 요청 ID 설정
                request_id = request.headers.get("x-request-id", generate_request_id())
                set_request_id(request_id)
                
                # 세션 ID 설정
                session_id = request.cookies.get("sid", generate_session_id())
                set_session_id(session_id)
                
                # 응답 헤더에 요청 ID 추가
                response = await call_next(request)
                response.headers["x-request-id"] = request_id
                
                return response
        
        return CorrelationMiddleware
    except ImportError:
        # FastAPI가 없는 경우 None 반환
        return None

def test_context():
    """컨텍스트 시스템을 테스트합니다."""
    # 기본값 테스트
    assert get_request_id() == "-"
    assert get_session_id() == "-"
    assert get_learning_session_id() == "-"
    assert get_phase() == "-"
    
    # 설정 테스트
    set_request_id("req123")
    set_session_id("sess456")
    set_learning_session_id("learn789")
    set_phase("training")
    
    assert get_request_id() == "req123"
    assert get_session_id() == "sess456"
    assert get_learning_session_id() == "learn789"
    assert get_phase() == "training"
    
    # 컨텍스트 딕셔너리 테스트
    ctx = get_context()
    assert ctx["request_id"] == "req123"
    assert ctx["session_id"] == "sess456"
    assert ctx["learning_session_id"] == "learn789"
    assert ctx["phase"] == "training"
    
    # 초기화 테스트
    clear_context()
    assert get_request_id() == "-"
    assert get_session_id() == "-"
    assert get_learning_session_id() == "-"
    assert get_phase() == "-"
    
    print("✅ 컨텍스트 시스템 테스트 통과")
    return True

if __name__ == "__main__":
    test_context()

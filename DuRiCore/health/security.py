#!/usr/bin/env python3
"""
DuRi 보안 모듈 - Bearer 토큰 검증
"""

import os
from fastapi import HTTPException, Header
from typing import Optional

def require_bearer_token(authorization: Optional[str] = Header(None, alias="Authorization")) -> bool:
    """Bearer 토큰 검증"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    token = authorization.split(" ", 1)[1]  # "Bearer " 제거
    expected_token = os.getenv("DURI_READONLY_TOKEN", "duri-canary-readonly-token")
    
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    return True

def require_canary_token(authorization: Optional[str] = Header(None, alias="Authorization")) -> bool:
    """카나리 전용 토큰 검증"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    token = authorization.split(" ", 1)[1]  # "Bearer " 제거
    expected_token = os.getenv("CANARY_TOKEN", "duri-canary-readonly-token")
    
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid canary token")
    
    return True

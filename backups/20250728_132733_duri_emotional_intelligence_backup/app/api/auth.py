from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from ..services.auth_service import get_auth_service
from ..models.user_model import UserLogin, UserResponse, Token, TokenRefreshRequest, TokenRefreshResponse

logger = logging.getLogger(__name__)

router = APIRouter()

auth_service = get_auth_service()

@router.post("/login", response_model=Token, tags=["auth"])
async def login(request: Request, login_data: UserLogin):
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다")
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60*30  # 30분
    )

@router.get("/me", response_model=UserResponse, tags=["auth"])
async def get_me(Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다 (Authorization: Bearer ...)")
    
    token = Authorization.split(" ", 1)[1]
    user = auth_service.get_current_user(token)

    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/refresh", response_model=TokenRefreshResponse, tags=["auth"])
async def refresh_token(request: Request, refresh: TokenRefreshRequest):
    new_access_token = auth_service.refresh_access_token(refresh.refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 리프레시 토큰입니다")
    return TokenRefreshResponse(
        access_token=new_access_token,
        expires_in=60*30
    ) 
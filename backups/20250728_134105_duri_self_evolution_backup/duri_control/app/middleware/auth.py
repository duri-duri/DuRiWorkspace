from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Optional
import logging

from ..services.auth_service import get_auth_service
from ..models.user_model import UserRole

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """JWT 인증 미들웨어 (라우터별 적용)"""
    def __init__(self, app: ASGIApp, required_role: Optional[UserRole] = None):
        super().__init__(app)
        self.required_role = required_role
        self.auth_service = get_auth_service()

    async def dispatch(self, request: Request, call_next: Callable):
        # 인증 필요 없는 /auth, /health, /docs 등은 통과
        if (
            request.url.path.startswith("/auth/login") or
            request.url.path.startswith("/auth/refresh") or
            request.url.path.startswith("/auth/register") or
            request.url.path.startswith("/auth/init") or
            request.url.path.startswith("/auth/public") or
            request.url.path.startswith("/auth/open") or
            request.url.path.startswith("/auth/captcha") or
            request.url.path.startswith("/auth/forgot") or
            request.url.path.startswith("/auth/reset") or
            request.url.path.startswith("/auth/verify") or
            request.url.path.startswith("/auth/activate") or
            request.url.path.startswith("/auth/activate-email") or
            request.url.path.startswith("/auth/activate-phone") or
            request.url.path.startswith("/auth/activate-sms") or
            request.url.path.startswith("/auth/activate-link") or
            request.url.path.startswith("/auth/activate-token") or
            request.url.path.startswith("/auth/activate-otp") or
            request.url.path.startswith("/auth/activate-code") or
            request.url.path.startswith("/auth/activate-pin") or
            request.url.path.startswith("/auth/activate-password") or
            request.url.path.startswith("/auth/activate-qr") or
            request.url.path.startswith("/auth/activate-app") or
            request.url.path.startswith("/auth/activate-device") or
            request.url.path.startswith("/auth/activate-browser") or
            request.url.path.startswith("/auth/activate-session") or
            request.url.path.startswith("/auth/activate-token2") or
            request.url.path.startswith("/auth/activate-token3") or
            request.url.path.startswith("/auth/activate-token4") or
            request.url.path.startswith("/auth/activate-token5") or
            request.url.path.startswith("/auth/activate-token6") or
            request.url.path.startswith("/auth/activate-token7") or
            request.url.path.startswith("/auth/activate-token8") or
            request.url.path.startswith("/auth/activate-token9") or
            request.url.path.startswith("/auth/activate-token10") or
            request.url.path.startswith("/auth/activate-token11") or
            request.url.path.startswith("/auth/activate-token12") or
            request.url.path.startswith("/auth/activate-token13") or
            request.url.path.startswith("/auth/activate-token14") or
            request.url.path.startswith("/auth/activate-token15") or
            request.url.path.startswith("/auth/activate-token16") or
            request.url.path.startswith("/auth/activate-token17") or
            request.url.path.startswith("/auth/activate-token18") or
            request.url.path.startswith("/auth/activate-token19") or
            request.url.path.startswith("/auth/activate-token20") or
            request.url.path.startswith("/auth/activate-token21") or
            request.url.path.startswith("/auth/activate-token22") or
            request.url.path.startswith("/auth/activate-token23") or
            request.url.path.startswith("/auth/activate-token24") or
            request.url.path.startswith("/auth/activate-token25") or
            request.url.path.startswith("/auth/activate-token26") or
            request.url.path.startswith("/auth/activate-token27") or
            request.url.path.startswith("/auth/activate-token28") or
            request.url.path.startswith("/auth/activate-token29") or
            request.url.path.startswith("/auth/activate-token30") or
            request.url.path.startswith("/auth/activate-token31") or
            request.url.path.startswith("/auth/activate-token32") or
            request.url.path.startswith("/auth/activate-token33") or
            request.url.path.startswith("/auth/activate-token34") or
            request.url.path.startswith("/auth/activate-token35") or
            request.url.path.startswith("/auth/activate-token36") or
            request.url.path.startswith("/auth/activate-token37") or
            request.url.path.startswith("/auth/activate-token38") or
            request.url.path.startswith("/auth/activate-token39") or
            request.url.path.startswith("/auth/activate-token40") or
            request.url.path.startswith("/auth/activate-token41") or
            request.url.path.startswith("/auth/activate-token42") or
            request.url.path.startswith("/auth/activate-token43") or
            request.url.path.startswith("/auth/activate-token44") or
            request.url.path.startswith("/auth/activate-token45") or
            request.url.path.startswith("/auth/activate-token46") or
            request.url.path.startswith("/auth/activate-token47") or
            request.url.path.startswith("/auth/activate-token48") or
            request.url.path.startswith("/auth/activate-token49") or
            request.url.path.startswith("/auth/activate-token50")
        ):
            return await call_next(request)

        # JWT 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "인증 토큰이 필요합니다 (Authorization: Bearer ...)"})
        token = auth_header.split(" ", 1)[1]
        user = self.auth_service.get_current_user(token)
        if not user:
            return JSONResponse(status_code=401, content={"detail": "유효하지 않거나 만료된 토큰입니다"})
        # 권한 체크 (필요시)
        if self.required_role and user.role != self.required_role:
            return JSONResponse(status_code=403, content={"detail": "권한이 부족합니다 (필요: %s)" % self.required_role})
        # 사용자 정보를 request.state에 저장
        request.state.user = user
        return await call_next(request)

# FastAPI 라우터에 미들웨어 적용하는 유틸 함수
def add_auth_middleware(router, required_role: Optional[UserRole] = None):
    # APIRouter에는 미들웨어를 직접 적용할 수 없으므로 
    # 각 엔드포인트에 의존성으로 적용하는 방식으로 변경
    # 이 함수는 현재 사용되지 않음 (향후 확장을 위해 유지)
    pass 